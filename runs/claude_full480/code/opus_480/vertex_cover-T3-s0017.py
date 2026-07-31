import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0, 3), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 5)]
    n = len(problem_qubits)
    k = 4

    edge_anc = ancilla_qubits[:len(edges)]        # 9 ancillas, one per edge
    count_anc = ancilla_qubits[len(edges):]       # remaining ancillas for counting
    # We need: all edges covered  AND  popcount(x) <= k.

    # --- compute edge-cover flags: edge_anc[e] = 1 iff edge e is covered ---
    def compute_edges():
        for e, (u, v) in enumerate(edges):
            a = edge_anc[e]
            # OR(x_u, x_v) into a (a starts at 0): a = x_u OR x_v
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.x(a)
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])

    def uncompute_edges():
        for e in reversed(range(len(edges))):
            u, v = edges[e]
            a = edge_anc[e]
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])
            qc.ccx(problem_qubits[u], problem_qubits[v], a)
            qc.x(a)
            qc.x(problem_qubits[u])
            qc.x(problem_qubits[v])

    # --- weight predicate: popcount(x) <= 4  over 6 bits.
    # Equivalent: NOT( popcount >= 5 ) = NOT( at least 5 of 6 ones )
    # popcount>=5 means at most 1 zero. Zeros = x_i flipped.
    # popcount<=4  <=>  number of zeros >= 2.
    # We compute z_i = NOT x_i (zero indicators) and want (#zeros >= 2).
    # #zeros >= 2 is FALSE only when #zeros in {0,1}, i.e. popcount in {5,6}.
    # So weight_ok = NOT( popcount==6 OR popcount==5 ).
    # popcount==6: all six problem qubits are 1.
    # popcount==5: exactly one qubit is 0.
    # We'll build a "weight_bad" flag = (popcount>=5) into one ancilla, then
    # combine: mark iff (all edges covered) AND (weight_bad == 0).

    wbad = count_anc[0]  # weight_bad flag

    def compute_weight_bad():
        # popcount==6 term: all ones -> flip wbad
        qc.mcx(problem_qubits, wbad)
        # popcount==5 terms: exactly one zero. For each j, others all 1 and x_j=0.
        for j in range(n):
            controls = [problem_qubits[i] for i in range(n) if i != j]
            qc.x(problem_qubits[j])
            qc.mcx(controls + [problem_qubits[j]], wbad)
            qc.x(problem_qubits[j])

    def uncompute_weight_bad():
        for j in reversed(range(n)):
            controls = [problem_qubits[i] for i in range(n) if i != j]
            qc.x(problem_qubits[j])
            qc.mcx(controls + [problem_qubits[j]], wbad)
            qc.x(problem_qubits[j])
        qc.mcx(problem_qubits, wbad)

    # --- assemble ---
    compute_edges()
    compute_weight_bad()

    # phase target: all edge_anc == 1  AND  wbad == 0.
    # flip wbad so condition becomes all-ones controls.
    qc.x(wbad)
    all_controls = list(edge_anc) + [wbad]
    phase_target = count_anc[1]
    qc.mcx(all_controls, phase_target)
    qc.z(phase_target)
    qc.mcx(all_controls, phase_target)
    qc.x(wbad)

    uncompute_weight_bad()
    uncompute_edges()
