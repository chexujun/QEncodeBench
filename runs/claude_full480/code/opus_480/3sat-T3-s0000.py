from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    # 8 clause ancillas + 1 phase ancilla
    c = ancilla_qubits[:8]
    phase = ancilla_qubits[8]

    # Each clause: ancilla = OR of literals.
    # Compute OR(l0,l1,l2) into ancilla a (initially |0>):
    #   a = NOT( AND(NOT l0, NOT l1, NOT l2) )
    # Implement: set a=1, then flip a to 0 iff all literals false.
    # Literal true when: positive var qubit == 1, negative var qubit == 0.

    # clause definitions: list of (qubit, negated) literals
    clauses = [
        [(1, True), (5, False), (6, False)],   # NOT x1 OR x5 OR x6
        [(1, False), (3, False), (5, False)],   # x1 OR x3 OR x5
        [(0, False), (2, False), (4, False)],   # x0 OR x2 OR x4
        [(1, False), (2, True), (4, False)],    # x1 OR NOT x2 OR x4
        [(0, False), (2, False), (5, True)],    # x0 OR x2 OR NOT x5
        [(1, False), (2, False), (5, False)],   # x1 OR x2 OR x5
        [(2, False), (5, False), (6, False)],   # x2 OR x5 OR x6
        [(1, True), (2, True), (3, True)],      # NOT x1 OR NOT x2 OR NOT x3
    ]

    def compute_clause(a, lits):
        # a starts at |0>. We want a = OR of literals.
        # A literal is FALSE when its var-qubit is in the state that makes it false:
        #   positive literal false  <=> qubit == 0
        #   negative literal false  <=> qubit == 1
        # We flip controls so that "control qubit == 1" means "literal is false",
        # then a mcx flips a to 1 iff ALL literals false, then X inverts to get OR.
        controls = []
        for (q, neg) in lits:
            if not neg:
                # positive literal false when qubit==0 -> X to map false->1
                qc.x(p[q])
            controls.append(p[q])
        qc.mcx(controls, a)          # a = 1 iff all literals false
        for (q, neg) in lits:
            if not neg:
                qc.x(p[q])           # restore
        qc.x(a)                      # a = OR of literals

    def uncompute_clause(a, lits):
        qc.x(a)
        controls = []
        for (q, neg) in lits:
            if not neg:
                qc.x(p[q])
            controls.append(p[q])
        qc.mcx(controls, a)
        for (q, neg) in lits:
            if not neg:
                qc.x(p[q])

    # compute all clause ancillas
    for a, lits in zip(c, clauses):
        compute_clause(a, lits)

    # phase: -1 iff all clause ancillas are 1 (formula satisfied)
    qc.h(phase)
    qc.mcx(c, phase)
    qc.h(phase)

    # uncompute clause ancillas (reverse order)
    for a, lits in reversed(list(zip(c, clauses))):
        uncompute_clause(a, lits)
