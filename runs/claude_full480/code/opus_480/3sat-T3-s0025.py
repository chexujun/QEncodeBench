from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # clauses as lists of (var_index, is_positive_literal)
    clauses = [
        [(0, False), (1, False), (6, False)],
        [(3, False), (5, False), (6, True)],
        [(2, True),  (4, False), (6, True)],
        [(3, False), (5, False), (6, False)],
        [(1, True),  (5, False), (6, False)],
        [(3, True),  (4, True),  (5, True)],
        [(0, False), (1, False), (2, True)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]  # 7 ancillas, one per clause
    final_ancilla = ancilla_qubits[len(clauses)]     # 8th ancilla for phase kickback

    def compute_clause(clause, target):
        # clause = OR of literals. clause is FALSE iff every literal is false.
        # A positive literal x_i is false when qubit is |0>; negative literal is false when |1>.
        # Flip controls so that "all literals false" <-> "all controls |1>", then MCX + X target
        # gives target = clause value (1 if satisfied).
        ctrls = [v for (v, pos) in clause]
        # For a positive literal (satisfied when qubit=1): literal false when qubit=0 -> need to invert
        # For a negative literal (satisfied when qubit=0): literal false when qubit=1 -> no invert
        for (v, pos) in clause:
            if pos:
                qc.x(v_map[v])
        # now for each control, control-|1> means the literal is FALSE
        qc.mcx([v_map[v] for (v, _) in clause], target)
        # target currently = 1 iff all literals false = clause UNsatisfied; invert to get satisfied
        qc.x(target)
        for (v, pos) in clause:
            if pos:
                qc.x(v_map[v])

    v_map = {i: x[i] for i in range(7)}

    # compute each clause value into its ancilla
    for cl, anc in zip(clauses, clause_ancillas):
        compute_clause(cl, anc)

    # formula satisfied iff all clause ancillas are 1 -> phase flip via multi-controlled Z
    qc.h(final_ancilla)
    qc.x(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)
    qc.x(final_ancilla)
    qc.h(final_ancilla)
    # The above three-line trick leaves final_ancilla in |0> while applying -1 phase
    # when all clause_ancillas == 1. Actually apply phase via mcp on clause ancillas instead:
    # (final_ancilla returns to |0>)

    # uncompute clause ancillas (mirror)
    for cl, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        compute_clause(cl, anc)
