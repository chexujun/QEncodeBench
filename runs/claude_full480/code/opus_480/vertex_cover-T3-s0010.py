from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1),(0,2),(0,3),(0,5),(1,2),(1,3),(1,4),(1,5),(3,5),(4,5)]
    n = len(problem_qubits)
    edge_anc = ancilla_qubits[:len(edges)]  # 10 ancillas, one per edge
    # remaining ancillas for count/threshold logic
    work = ancilla_qubits[len(edges):]      # 3 ancillas

    def compute_edges():
        # edge covered = u OR v = NOT(NOT u AND NOT v)
        for (u, v), a in zip(edges, edge_anc):
            qu = problem_qubits[u]
            qv = problem_qubits[v]
            qc.x(qu); qc.x(qv)
            qc.ccx(qu, qv, a)   # a = (NOT u)AND(NOT v) after flips -> uncovered
            qc.x(qu); qc.x(qv)
            qc.x(a)             # a = covered
        # now all edge_anc == 1 iff every edge covered

    def uncompute_edges():
        for (u, v), a in zip(edges, edge_anc):
            qu = problem_qubits[u]
            qv = problem_qubits[v]
            qc.x(a)
            qc.x(qu); qc.x(qv)
            qc.ccx(qu, qv, a)
            qc.x(qu); qc.x(qv)

    # Popcount <= 4  over 6 bits  <=>  NOT (popcount >= 5)
    # popcount >= 5 means at least 5 of 6 bits are 1.
    # Equivalent: at most one bit is 0. i.e. number of zeros <= 1.
    # We will build predicate P = (all edges covered) AND (weight <= 4).
    # weight <= 4  <=>  NOT( weight==5 OR weight==6 ).
    # weight>=5 : at most one zero among 6 bits.
    # Let's compute "count_ge5" flag using symmetric reasoning via zeros.
    # zeros z_i = NOT x_i. weight>=5 <=> sum z_i <= 1 <=> at most one zero.
    # "at most one zero" is hard; instead directly test weight>=5 =
    #   OR over choices of 5 bits all being 1.
    # There are C(6,5)=6 terms of AND of 5 bits, plus the all-6 term is subsumed.
    # weight>=5 = OR_{j} (AND of all bits except bit j) [that gives >=5].
    # Implement flag5 in work[0] as OR of 6 AND-of-5 terms.

    def and_of_all_except(j, target):
        # target ^= AND of x_i for i != j  (5 controls)
        ctrls = [problem_qubits[i] for i in range(n) if i != j]
        qc.mcx(ctrls, target)

    def compute_ge5(target):
        # target = OR_j term_j ; use inclusion via building on |0>:
        # OR = NOT AND NOT. Simpler: target ^= term_j sequentially only works
        # if terms are mutually exclusive. The 6 terms (weight>=5 subsets):
        # term_j true means all bits except j are 1 (bit j arbitrary).
        # If weight==6, every term_j is true -> XOR of 6 ones = 0. BAD.
        # So use OR construction with a clean flag via De Morgan on |0>.
        # Build NOT-target starting at 1: we want target = OR terms.
        # Do: target=1; for each term, target = target AND NOT term? messy.
        # Instead: weight>=5 <=> weight==5 XOR weight==6? No.
        # Use: flag6 = AND all 6 bits; flag_exactly5 = XOR-safe.
        pass

    # Cleaner: weight<=4 <=> at least two bits are 0 <=> zeros>=2.
    # zeros>=2 = OR over pairs? C(6,2)=15 terms, messy.
    # Use threshold via exact indicator: weight<=4 = NOT(weight==5) AND NOT(weight==6).
    # weight==6 = AND all 6 bits.
    # weight==5 = OR_j (all except j are 1 AND bit j is 0).
    #   these 6 terms ARE mutually exclusive (differ in which bit is 0),
    #   so XOR == OR here. And weight==6 is excluded (bit j=1 fails).
    compute_edges()

    w0 = work[0]  # flag: weight==6
    w1 = work[1]  # flag: weight==5 (mutually exclusive terms -> xor ok)
    w2 = work[2]  # final predicate flag

    # w0 = AND all 6 bits
    qc.mcx([problem_qubits[i] for i in range(n)], w0)

    # w1 = OR/XOR_j ( x_j==0 AND others==1 )
    for j in range(n):
        qc.x(problem_qubits[j])
        ctrls = [problem_qubits[i] for i in range(n)]  # after flip, need all==1
        qc.mcx(ctrls, w1)
        qc.x(problem_qubits[j])

    # weight<=4  <=>  NOT w0 AND NOT w1
    # predicate P = edges_all_covered AND (NOT w0) AND (NOT w1)
    # edges_all_covered = all edge_anc == 1
    # Build controls: edge_anc (all 1) + w0 (must be 0) + w1 (must be 0)
    qc.x(w0); qc.x(w1)
    qc.mcx(edge_anc + [w0, w1], w2)
    qc.x(w0); qc.x(w1)

    # phase
    qc.z(w2)

    # uncompute w2
    qc.x(w0); qc.x(w1)
    qc.mcx(edge_anc + [w0, w1], w2)
    qc.x(w0); qc.x(w1)

    # uncompute w1
    for j in range(n):
        qc.x(problem_qubits[j])
        qc.mcx([problem_qubits[i] for i in range(n)], w1)
        qc.x(problem_qubits[j])

    # uncompute w0
    qc.mcx([problem_qubits[i] for i in range(n)], w0)

    uncompute_edges()
