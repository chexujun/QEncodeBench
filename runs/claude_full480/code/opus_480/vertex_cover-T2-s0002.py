from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4)]
    n = len(problem_qubits)
    k = 3

    edge_anc = ancilla_qubits[:len(edges)]        # 6 ancillas, one per edge
    count_anc = ancilla_qubits[len(edges):len(edges) + 3]  # 3 ancillas for popcount (values 0..5 need 3 bits)
    cover_flag = edge_anc  # reuse naming clarity

    def compute():
        # 1) For each edge, edge_anc = OR(u, v) = 1 iff edge covered.
        # OR(a,b) = NOT( AND(NOT a, NOT b) ). Compute into ancilla (init 0):
        # set ancilla to 1, then if both endpoints are 0 flip it to 0.
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(a)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(problem_qubits[v])
            qc.x(problem_qubits[u])

        # 2) Popcount of the 5 problem qubits into a 3-bit counter (count_anc).
        # Ripple increment for each problem qubit.
        c0, c1, c2 = count_anc[0], count_anc[1], count_anc[2]
        for q in problem_qubits:
            # increment 3-bit counter conditioned on q
            # carry logic: bit2 ^= q & c1 & c0 ; bit1 ^= q & c0 ; bit0 ^= q
            qc.mcx([q, c0, c1], c2)
            qc.ccx(q, c0, c1)
            qc.cx(q, c0)

    def uncompute():
        c0, c1, c2 = count_anc[0], count_anc[1], count_anc[2]
        for q in reversed(problem_qubits):
            qc.cx(q, c0)
            qc.ccx(q, c0, c1)
            qc.mcx([q, c0, c1], c2)
        for i in reversed(range(len(edges))):
            u, v = edges[i]
            a = edge_anc[i]
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(problem_qubits[v])
            qc.x(problem_qubits[u])
            qc.x(a)

    compute()

    # Phase condition: all edges covered (all edge_anc == 1) AND count <= 3.
    # count <= 3 means NOT(count >= 4) = NOT(c2==1 and (c1==1 or c0==1))... 
    # count in 0..5. count>=4 iff c2==1 and (c1 or c0). count==4 -> 100? bits: c0 is LSB.
    # value = c0 + 2*c1 + 4*c2. count<=3 iff value<4 iff c2==0.
    # (max count is 5 = 101, so c2==1 means value>=4). So condition: c2 == 0.
    c2 = count_anc[2]

    # Apply -1 phase iff all edge_anc==1 AND c2==0.
    # Flip c2 so we can require it ==1 in the control set.
    qc.x(c2)
    controls = list(edge_anc) + [c2]
    # multi-controlled Z via H-MCX-H on last target, or mcp(pi). Use mcp.
    qc.mcp(math.pi, controls[:-1], controls[-1])
    qc.x(c2)

    uncompute()
