from qiskit import QuantumCircuit
from math import pi


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    edges = [(0, 1), (1, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (3, 5), (4, 5)]

    edge_anc = ancilla_qubits[0:9]        # one ancilla per edge (OR of endpoints)
    cnt = ancilla_qubits[9:12]            # 3-bit popcount accumulator (0..6 -> needs 3 bits)
    all_ok = ancilla_qubits[9]            # reuse later; but keep separate: use a dedicated flag

    # We need: (all edges covered) AND (popcount(x) <= 3).
    # Ancilla budget: 12. Use 9 for edges. That leaves 3 for the counter.
    # Compute edge-cover flags into edge_anc: edge_anc[j] = a OR b.
    def edge_or(j, on):
        a, b = edges[j]
        anc = edge_anc[j]
        if on:
            # anc = a OR b = NOT( NOT a AND NOT b )
            qc.x(p[a]); qc.x(p[b])
            qc.ccx(p[a], p[b], anc)
            qc.x(anc)
            qc.x(p[a]); qc.x(p[b])
        else:
            qc.x(p[a]); qc.x(p[b])
            qc.x(anc)
            qc.ccx(p[a], p[b], anc)
            qc.x(p[a]); qc.x(p[b])

    for j in range(9):
        edge_or(j, True)

    # popcount(x) <= 3  <=>  NOT( popcount(x) >= 4 ).
    # Build a 3-bit ripple counter cnt[0..2] (LSB..MSB) counting the six problem bits.
    # Adding a single bit q to a 3-bit counter:
    #   carry from bit0: cnt0 & q ; etc.  Implement increment-by-qubit.
    c0, c1, c2 = cnt

    def add_bit(q, on):
        # increment 3-bit counter (c0 lsb) by q, controlled add.
        # order matters: update high bits first using ANDs, then low bit.
        if on:
            qc.ccx(q, c1, c2)      # carry into c2 if bit1 set and adding
            qc.ccx(q, c0, c1)      # carry into c1 if bit0 set and adding
            qc.cx(q, c0)           # add into c0
        else:
            qc.cx(q, c0)
            qc.ccx(q, c0, c1)
            qc.ccx(q, c1, c2)

    for i in range(6):
        add_bit(p[i], True)

    # Now cnt holds popcount(x) in binary (mod 8; max 6 so exact).
    # popcount <= 3 means value in {0,1,2,3} => c2 == 0.
    # So the size constraint predicate is simply (c2 == 0).
    # Full predicate = (all edge_anc == 1) AND (c2 == 0).
    # Apply phase -1 when all edge_anc are 1 AND c2 is 0.
    # Controls: 9 edge_anc (want =1), plus c2 (want =0 -> control on X-ed c2).
    qc.x(c2)
    controls = list(edge_anc) + [c2]
    qc.h(all_ok if False else edge_anc[0])  # no-op guard removed below
    # Use multi-controlled Z via H-MCX-H on the last control? Simpler: mcp(pi,...).
    qc.mcp(pi, controls[:-1], controls[-1])
    qc.x(c2)

    # Uncompute counter
    for i in reversed(range(6)):
        add_bit(p[i], False)

    # Uncompute edges
    for j in reversed(range(9)):
        edge_or(j, False)
