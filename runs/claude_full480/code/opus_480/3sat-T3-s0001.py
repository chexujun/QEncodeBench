import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    x = problem_qubits
    cl_anc = ancilla_qubits[:7]
    out = ancilla_qubits[7]

    # Each clause: (literals). literal = (qubit_index, negated?)
    # We compute clause satisfaction into a clause-ancilla.
    # A 3-literal OR clause is FALSE iff all three literals are FALSE.
    # We use an mcx: set ancilla to 1 when clause is TRUE.
    # Trick: prepare each literal so that literal-FALSE => qubit==1 after local X,
    # then clause FALSE iff all three ==1. mcx flips clause-anc to 1 (=NOT-all-false region),
    # combined with an initial X so ancilla starts 1 (TRUE) then set to 0 when all-false.

    clauses = [
        [(3, False), (4, True), (7, True)],
        [(2, False), (4, False), (7, True)],
        [(2, False), (3, False), (6, False)],
        [(2, False), (3, True), (6, False)],
        [(1, True), (4, True), (5, False)],
        [(3, False), (6, False), (7, False)],
        [(0, True), (3, True), (4, True)],
    ]

    def lit_false_flips(lit):
        # After applying these X's, the literal being FALSE corresponds to qubit == 1.
        # literal (i, negated=False) = x_i ; FALSE when x_i==0 -> X to make it 1.
        # literal (i, negated=True) = NOT x_i ; FALSE when x_i==1 -> no X.
        qi, neg = lit
        return not neg  # apply X if positive literal

    # compute clause ancillas
    for c_idx, clause in enumerate(clauses):
        anc = cl_anc[c_idx]
        controls = []
        for lit in clause:
            qi = lit[0]
            if lit_false_flips(lit):
                qc.x(x[qi])
            controls.append(x[qi])
        # start clause anc at 1 (TRUE)
        qc.x(anc)
        # if all controls==1 (all literals false), flip anc to 0
        qc.mcx(controls, anc)
        # restore X's on inputs
        for lit in clause:
            qi = lit[0]
            if lit_false_flips(lit):
                qc.x(x[qi])

    # formula TRUE iff all clause ancillas == 1. Phase -1 on that.
    qc.h(out)
    qc.x(out)
    qc.mcx(cl_anc, out)
    qc.x(out)
    qc.h(out)

    # uncompute clause ancillas (mirror)
    for c_idx in reversed(range(len(clauses))):
        clause = clauses[c_idx]
        anc = cl_anc[c_idx]
        controls = []
        for lit in clause:
            qi = lit[0]
            if lit_false_flips(lit):
                qc.x(x[qi])
            controls.append(x[qi])
        qc.mcx(controls, anc)
        qc.x(anc)
        for lit in clause:
            qi = lit[0]
            if lit_false_flips(lit):
                qc.x(x[qi])
