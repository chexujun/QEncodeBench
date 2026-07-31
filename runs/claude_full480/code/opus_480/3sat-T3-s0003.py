import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:7]
    out = ancilla_qubits[7]

    # Each clause: (literals). literal = (qubit_index, negated?)
    # clause satisfied unless all literals false.
    # Compute clause result into cl[j]: cl[j]=1 iff clause satisfied.
    clauses = [
        [(1, True), (3, False), (4, False)],
        [(1, False), (5, False), (6, True)],
        [(0, True), (3, True), (4, True)],
        [(0, True), (1, True), (6, True)],
        [(1, False), (4, True), (6, False)],
        [(0, True), (1, True), (3, False)],
        [(2, False), (5, True), (6, True)],
    ]

    def compute_clause(lits, target):
        # Set literal-controls: literal true. For a positive literal x_i,
        # control on x_i=1; for negative, control on x_i=0.
        # Clause is UNSAT iff every literal is false => controls where each
        # literal-false. literal false: positive -> x_i=0, negative -> x_i=1.
        # We flip target if all-false, then X to make target=1 when SAT.
        ctrls = []
        for (qi, neg) in lits:
            ctrls.append(x[qi])
            if not neg:
                # positive literal false means x_i=0; want control on 0 => X wrap
                qc.x(x[qi])
            # negative literal false means x_i=1; control on 1 (no wrap)
        qc.mcx(ctrls, target)  # target ^= (all literals false)
        for (qi, neg) in lits:
            if not neg:
                qc.x(x[qi])
        qc.x(target)  # target = 1 iff clause satisfied

    for j, lits in enumerate(clauses):
        compute_clause(lits, cl[j])

    # AND of all clause results -> phase
    qc.h(out)
    qc.mcx(cl, out)
    qc.h(out)

    # Uncompute clauses (mirror)
    def uncompute_clause(lits, target):
        qc.x(target)
        ctrls = []
        for (qi, neg) in lits:
            ctrls.append(x[qi])
            if not neg:
                qc.x(x[qi])
        qc.mcx(ctrls, target)
        for (qi, neg) in lits:
            if not neg:
                qc.x(x[qi])

    for j in reversed(range(len(clauses))):
        uncompute_clause(clauses[j], cl[j])
