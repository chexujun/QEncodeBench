from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    anc = ancilla_qubits

    # Clauses as (variable_index, is_positive) literals.
    clauses = [
        [(1, True), (2, True), (5, True)],
        [(1, False), (2, True), (4, False)],
        [(0, False), (1, False), (3, False)],
        [(2, True), (4, False), (5, False)],
        [(1, True), (4, True), (5, False)],
    ]

    def clause_compute(clause, target):
        # Compute OR of literals into target ancilla (target assumed |0>).
        # OR(l0,l1,l2) = NOT(AND(NOT l0, NOT l1, NOT l2)).
        # For each literal, the qubit is "false" (violates clause) when:
        #   positive literal -> qubit is 0, negative literal -> qubit is 1.
        # We want target = 1 iff clause satisfied.
        # Strategy: set target=1, then flip target to 0 only when ALL literals false.
        # Use mcx controlled on the "all literals false" condition.
        ctrls = []
        flips = []  # qubits we X to make control-active when literal is false
        for (vi, pos) in clause:
            q = x[vi]
            ctrls.append(q)
            if pos:
                # literal false when q==0 -> need control active on 0 -> X the qubit
                flips.append(q)
        # Apply X to flips so that mcx triggers exactly when all literals are false.
        for q in flips:
            qc.x(q)
        # target starts |0>; set to 1
        qc.x(target)
        # if all literals false, flip target back to 0
        qc.mcx(ctrls, target)
        # undo flips
        for q in flips:
            qc.x(q)

    def clause_uncompute(clause, target):
        ctrls = []
        flips = []
        for (vi, pos) in clause:
            q = x[vi]
            ctrls.append(q)
            if pos:
                flips.append(q)
        for q in flips:
            qc.x(q)
        qc.mcx(ctrls, target)
        qc.x(target)
        for q in flips:
            qc.x(q)

    # Compute each clause satisfaction into its own ancilla.
    for i, clause in enumerate(clauses):
        clause_compute(clause, anc[i])

    # Phase: -1 iff all clause ancillas are 1 (formula satisfied).
    # Use multi-controlled Z via mcp with pi on all clause ancillas.
    clause_ancillas = [anc[i] for i in range(len(clauses))]
    qc.h(clause_ancillas[-1])
    qc.mcx(clause_ancillas[:-1], clause_ancillas[-1])
    qc.h(clause_ancillas[-1])

    # Uncompute clause ancillas.
    for i, clause in reversed(list(enumerate(clauses))):
        clause_uncompute(clause, anc[i])
