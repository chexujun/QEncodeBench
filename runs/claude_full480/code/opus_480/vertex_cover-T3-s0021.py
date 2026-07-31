from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Graph edges
    edges = [(0, 1), (1, 2), (1, 4), (1, 5), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]
    q = problem_qubits  # 6 problem qubits (vertices)
    # 12 ancillas: use first 9 as per-edge covered flags, next 3 for popcount / size check,
    # remaining as scratch for the final AND.
    edge_anc = ancilla_qubits[0:9]     # one ancilla per edge (covered flag)
    cnt = ancilla_qubits[9:12]         # 3-bit counter for Hamming weight (0..6 needs 3 bits)
    scratch = ancilla_qubits[9:12]     # reuse naming; we manage carefully below

    # ---- COMPUTE: per-edge "covered" flags ----
    # edge covered iff (x_u OR x_v). Compute OR into an ancilla starting at |0>:
    # anc = x_u OR x_v  ==  NOT( (NOT x_u) AND (NOT x_v) )
    # Implement: X(u); X(v); ccx(u,v,anc); X(anc); X(u); X(v)  => anc = OR
    for (u, v), a in zip(edges, edge_anc):
        qc.x(q[u]); qc.x(q[v])
        qc.ccx(q[u], q[v], a)
        qc.x(a)
        qc.x(q[u]); qc.x(q[v])

    # ---- COMPUTE: Hamming weight of x into 3-bit counter cnt[0..2] (little-endian) ----
    # Add each x_i into the counter via a ripple increment controlled on x_i.
    # Incrementing a 3-bit register controlled on ctrl:
    #   carry into bit2 first: cnt2 ^= ctrl & cnt1 & cnt0
    #   cnt1 ^= ctrl & cnt0
    #   cnt0 ^= ctrl
    c0, c1, c2 = cnt[0], cnt[1], cnt[2]
    for i in range(6):
        ctrl = q[i]
        qc.mcx([ctrl, c1, c0], c2)
        qc.ccx(ctrl, c0, c1)
        qc.cx(ctrl, c0)

    # size <= 3 means NOT (count >= 4) and NOT (count in {4,5,6}); with 3-bit counter
    # (values 0..6), count <= 3 iff bit2 (value 4) is 0 UNLESS count==... actually
    # count in 0..6: bit2=1 means count in {4,5,6,7}=>{4,5,6}. So size<=3 iff c2==0.
    # size_ok flag = NOT c2.

    # ---- Multi-controlled phase: mark iff all 9 edge flags == 1 AND c2 == 0 ----
    # Controls: all edge_anc must be 1; c2 must be 0 (control on |0> => X then control then X).
    controls = list(edge_anc)
    qc.x(c2)                      # so that control-on-1 corresponds to original c2==0
    controls.append(c2)
    # apply Z phase controlled on all controls: use H-MCX-H = MCZ equivalently mcp(pi)
    qc.h(controls[-1])
    qc.mcx(controls[:-1], controls[-1])
    qc.h(controls[-1])
    qc.x(c2)                      # restore

    # ---- UNCOMPUTE (mirror) ----
    # Uncompute counter (reverse order)
    for i in reversed(range(6)):
        ctrl = q[i]
        qc.cx(ctrl, c0)
        qc.ccx(ctrl, c0, c1)
        qc.mcx([ctrl, c1, c0], c2)

    # Uncompute edge flags
    for (u, v), a in zip(edges, edge_anc):
        qc.x(q[u]); qc.x(q[v])
        qc.x(a)
        qc.ccx(q[u], q[v], a)
        qc.x(q[u]); qc.x(q[v])
