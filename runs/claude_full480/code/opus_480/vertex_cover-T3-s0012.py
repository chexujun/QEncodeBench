import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 4), (1, 5), (2, 3), (2, 5), (3, 5)]
    n = len(problem_qubits)  # 6
    k = 3

    # Ancilla layout:
    # 6 edge-cover ancillas, 3 popcount/comparison ancillas
    edge_anc = ancilla_qubits[0:6]   # one per edge: 1 iff edge covered
    cnt = ancilla_qubits[6:9]        # 3-bit counter of popcount (0..6 needs 3 bits)
    # We need popcount <= 3.  popcount ranges 0..6 -> 3 bits (values 0..7).
    # "size <= 3" <=> NOT (popcount >= 4) <=> bit2==0 OR (bit2==1 AND bit1==0 AND bit0==0)
    # i.e. value in {0,1,2,3} means bit2==0; value 4..6 has bit2==1.
    # So size<=3 <=> counter bit2 == 0.  (since max is 6 <=7, bit2 set exactly for 4,5,6)
    final = ancilla_qubits[8]  # reuse? no -- we need a clean mark qubit.

    # We'll use edge_anc (6) + a 3-bit counter (3) = 9 ancillas exactly.
    # But we also need to combine predicates onto a phase.  Use the fact:
    #   f = (all edges covered) AND (bit2 of popcount == 0)
    # Apply phase via a multi-controlled Z where the counter-bit2 acts as a
    # negative control (must be 0) and all edge ancillas as positive controls.

    def compute():
        # edge coverage: edge_anc[i] = u OR v = NOT(NOT u AND NOT v)
        for i, (u, v) in enumerate(edges):
            a = edge_anc[i]
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.x(a)
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
        # popcount into 3-bit counter cnt = [c0,c1,c2] (c0 LSB)
        for i in range(n):
            b = problem_qubits[i]
            # increment 3-bit counter controlled on b
            # carry chain: c2 ^= b & c1 & c0 ; c1 ^= b & c0 ; c0 ^= b
            qc.ccx(b, cnt[0], cnt[1]) if False else None
            # proper controlled increment:
            qc.mcx([b, cnt[0], cnt[1]], cnt[2])
            qc.ccx(b, cnt[0], cnt[1])
            qc.cx(b, cnt[0])

    compute()

    # phase: -1 iff all 6 edges covered AND cnt[2]==0
    controls = list(edge_anc)
    qc.x(cnt[2])  # turn negative control into positive
    qc.h(controls[-1])
    qc.mcx(controls[:-1] + [cnt[2]], controls[-1])
    qc.h(controls[-1])
    qc.x(cnt[2])

    # uncompute (mirror)
    for i in reversed(range(n)):
        b = problem_qubits[i]
        qc.cx(b, cnt[0])
        qc.ccx(b, cnt[0], cnt[1])
        qc.mcx([b, cnt[0], cnt[1]], cnt[2])
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        a = edge_anc[i]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.x(a)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
