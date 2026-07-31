from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    # clauses as list of (var_index, is_positive) literals
    clauses = [
        [(0, False), (1, True), (2, False)],
        [(1, False), (2, True), (4, True)],
        [(0, True), (1, False), (3, True)],
        [(1, False), (3, True), (4, False)],
        [(1, True), (2, False), (3, False)],
        [(1, False), (3, False), (4, True)],
    ]
    clause_anc = ancilla_qubits[:6]   # one ancilla per clause
    final_anc = ancilla_qubits[6]     # holds AND of all clauses

    def compute_clauses():
        for c, anc in zip(clauses, clause_anc):
            # clause is satisfied unless ALL literals are false.
            # literal (v, True) false when x_v == 0 ; (v, False) false when x_v == 1.
            # Flip qubits so that "all literals false" <=> all controls == 1.
            for v, pos in c:
                if pos:
                    qc.x(x[v])       # positive literal false when x_v==0 -> make it 1
            # now anc = NOT(all literals false) ; controls high mean literal false
            controls = [x[v] for v, pos in c]
            qc.mcx(controls, anc)    # anc = 1 iff all literals false (clause unsat)
            qc.x(anc)                # anc = 1 iff clause satisfied
            # restore flips
            for v, pos in c:
                if pos:
                    qc.x(x[v])

    def uncompute_clauses():
        for c, anc in zip(clauses, clause_anc):
            for v, pos in c:
                if pos:
                    qc.x(x[v])
            qc.x(anc)
            controls = [x[v] for v, pos in c]
            qc.mcx(controls, anc)
            for v, pos in c:
                if pos:
                    qc.x(x[v])

    compute_clauses()
    qc.mcx(clause_anc, final_anc)   # final = AND of all clause ancillas
    qc.z(final_anc)                 # phase -1 iff formula satisfied
    qc.mcx(clause_anc, final_anc)   # uncompute final
    uncompute_clauses()
