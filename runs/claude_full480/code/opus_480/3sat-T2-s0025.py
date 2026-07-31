import numpy as np
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # 5 clauses, each ORs 3 literals. Ancillas 0..4 hold clause satisfaction.
    # clause_ok = OR(literals). Compute via NOT(AND(negated literals)).
    # For each clause: for each literal, if literal is positive we need var True,
    # so the "false" condition is var==0 -> use var as-is into an AND of "all false".
    # We compute AND of (literal-is-false) into ancilla, then X to get clause-ok.

    clauses = [
        [(0, True),  (1, True),  (2, True)],
        [(0, False), (1, False), (2, False)],
        [(0, True),  (2, True),  (3, False)],
        [(0, True),  (2, False), (4, True)],
        [(0, False), (1, True),  (3, False)],
    ]

    clause_anc = ancilla_qubits[0:5]
    final_anc = ancilla_qubits[5]

    def compute_clause(ci):
        lits = clauses[ci]
        anc = clause_anc[ci]
        # literal is false when: positive literal and var==0, or negative literal and var==1.
        # We want anc = AND over literals of (literal_false). Then clause_ok = NOT anc.
        # literal_false control state: positive -> control on 0, negative -> control on 1.
        ctrl_state = ''
        ctrls = []
        for (v, pos) in lits:
            ctrls.append(x[v])
            # qiskit ctrl_state string is little-endian relative to control list order
            ctrl_state = ('0' if pos else '1') + ctrl_state
        qc.mcx(ctrls, anc, ctrl_state=ctrl_state)
        qc.x(anc)  # anc now = clause_ok

    def uncompute_clause(ci):
        lits = clauses[ci]
        anc = clause_anc[ci]
        qc.x(anc)
        ctrl_state = ''
        ctrls = []
        for (v, pos) in lits:
            ctrls.append(x[v])
            ctrl_state = ('0' if pos else '1') + ctrl_state
        qc.mcx(ctrls, anc, ctrl_state=ctrl_state)

    for ci in range(5):
        compute_clause(ci)

    qc.h(final_anc)
    qc.mcx(clause_anc, final_anc)
    qc.h(final_anc)

    for ci in range(4, -1, -1):
        uncompute_clause(ci)
