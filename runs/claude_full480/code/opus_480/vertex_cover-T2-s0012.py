from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3)]
    k = 3
    n = len(problem_qubits)

    edge_anc = ancilla_qubits[:len(edges)]            # 6 ancillas, one per edge
    count_anc = ancilla_qubits[len(edges):len(edges) + 2]  # 2 count qubits (weight up to 5 needs 3, but <=3 check uses overflow)
    final_anc = ancilla_qubits[len(edges) + 2]        # 1 predicate ancilla

    # We actually need to count popcount and compare <= 3.
    # popcount of 5 bits needs 3 bits (0..5). We have only 2 count ancillas + 1 final.
    # Re-plan: use 3 count qubits by borrowing edge ancillas after they are freed is unsafe
    # (must stay clean during phase). Instead allocate: 6 edge + 3 count = 9 ancillas, and
    # reuse one edge ancilla region? We have exactly 9 ancillas. Use 6 edges is not
    # simultaneously needed with count. So: compute count first into 3 count qubits using
    # 3 of the 9 ancillas, then compute edges reusing the other, all must be clean at phase.
    # Simplest correct: use 3 ancillas for a popcount adder, 5 edge... but edges=6.
    # We have 9 ancillas total. Plan: 3 for count register, 6 for edges -> 9. Then need
    # predicate ancilla too (10). So combine: compute predicate directly onto count MSB logic.

    cnt = ancilla_qubits[0:3]      # 3-bit popcount register (holds 0..5)
    edgeA = ancilla_qubits[3:9]    # 6 edge ancillas
    # predicate we fold by controlling phase on the AND of (all edges covered) and (count<=3).
    # count<=3 means MSB-of-count arrangement: value in {0,1,2,3} -> bit2==0 when value<4.
    # value 4 -> 100, value5 ->101 : bit2==1. So count<=3  <=>  cnt[2]==0.

    def add_one(control, reg):
        # controlled increment of 3-bit reg by 1 (ripple), controlled on `control`
        # increment: carry chain. reg[0] toggles; carry into reg[1] etc.
        # controlled version using ancilla-free ripple via multi-controls.
        qc.mcx([control, reg[0], reg[1]], reg[2])
        qc.ccx(control, reg[0], reg[1])
        qc.cx(control, reg[0])

    # compute popcount
    for q in problem_qubits:
        add_one(q, cnt)

    # compute edge coverage: edgeA[i] = x_u OR x_v = NOT( (1-x_u)(1-x_v) )
    for i, (u, v) in enumerate(edges):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        qc.x(qu); qc.x(qv)
        qc.ccx(qu, qv, edgeA[i])   # edgeA[i] = (1-x_u)&(1-x_v) = edge uncovered
        qc.x(qu); qc.x(qv)
        qc.x(edgeA[i])             # edgeA[i] = edge covered

    # predicate = (all edges covered) AND (cnt[2]==0)
    # controls: all edgeA[i]==1 and cnt[2]==0
    controls = list(edgeA)
    qc.x(cnt[2])                   # so control==1 means original cnt[2]==0
    controls.append(cnt[2])
    qc.h(problem_qubits[0])        # placeholder no-op removed below
    qc.h(problem_qubits[0])
    qc.mcp(math.pi, controls[:-1], controls[-1])  # phase -1 iff all controls==1
    qc.x(cnt[2])

    # uncompute edges
    for i, (u, v) in enumerate(edges):
        qu = problem_qubits[u]
        qv = problem_qubits[v]
        qc.x(edgeA[i])
        qc.x(qu); qc.x(qv)
        qc.ccx(qu, qv, edgeA[i])
        qc.x(qu); qc.x(qv)

    # uncompute popcount (reverse)
    for q in reversed(problem_qubits):
        qc.cx(q, cnt[0])
        qc.ccx(q, cnt[0], cnt[1])
        qc.mcx([q, cnt[0], cnt[1]], cnt[2])
