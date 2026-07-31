import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits

    # Each clause: list of (variable_index, negated_flag)
    # negated_flag True means the literal is NOT x_i, i.e. clause literal
    # is satisfied when x_i == 0.
    clauses = [
        [(0, False), (1, True),  (5, False)],
        [(2, True),  (3, True),  (4, False)],
        [(1, True),  (4, False), (5, False)],
        [(2, False), (4, False), (5, False)],
        [(0, True),  (3, True),  (5, False)],
        [(0, True),  (2, False), (6, True)],
        [(0, True),  (2, True),  (5, False)],
        [(1, False), (3, False), (4, True)],
        [(3, False), (4, False), (5, False)],
        [(2, False), (4, False), (6, True)],
        [(2, False), (3, True),  (6, False)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]  # 11 ancillas
    final_ancilla = ancilla_qubits[len(clauses)]     # 12th ancilla

    def compute_clause(clause, target):
        # A clause (OR of literals) is FALSE iff every literal is false.
        # Literal (i, neg): false when x_i == (0 if neg else 1)... careful:
        #   literal x_i        false when x_i == 0
        #   literal NOT x_i    false when x_i == 1
        # We set target = 1 iff clause is TRUE.
        # Strategy: flip control-qubit polarity so that "all literals false"
        # corresponds to all controls == 1, mcx sets target, then target
        # holds (clause false); we then X the target to invert -> clause true.
        controls = []
        flips = []
        for (i, neg) in clause:
            # literal false condition:
            #   neg=False (x_i): false when x_i==0  -> need X to make control=1
            #   neg=True (NOT x_i): false when x_i==1 -> control already 1
            if not neg:
                flips.append(x[i])
            controls.append(x[i])
        for q in flips:
            qc.x(q)
        qc.mcx(controls, target)   # target = 1 iff all literals false
        for q in flips:
            qc.x(q)
        qc.x(target)               # target = 1 iff clause true

    # Compute all clause satisfaction bits
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # AND of all clause bits into final_ancilla, then phase
    qc.mcx(clause_ancillas, final_ancilla)
    qc.z(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)

    # Uncompute clause bits (mirror)
    for clause, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        compute_clause(clause, anc)
