from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    # ancillas: one per clause (5) + one final target
    c = ancilla_qubits[0:5]
    tgt = ancilla_qubits[5]

    # Each clause OR(l_a, l_b, l_c) is TRUE unless all three literals are false.
    # We compute clause-satisfied bit into ancilla c[k] = 1 iff clause satisfied.
    # A literal "x" is false when qubit=0; literal "NOT x" is false when qubit=1.
    # Strategy: set clause ancilla to 1, then flip it to 0 iff all literals false
    # (i.e. the unsatisfying assignment). Use mcx conditioned on the negated
    # literal pattern by X-wrapping the qubits whose "false" value is 1.

    # clause definitions: (qubit, need_value_for_literal_false)
    # literal x_i false  -> qubit must be 0  -> to trigger mcx (all-ones control) X-wrap it
    # literal NOT x_i false -> qubit must be 1 -> no wrap
    clauses = [
        [(x0, 1), (x1, 0), (x3, 1)],   # NOT x0 OR x1 OR NOT x3
        [(x0, 1), (x2, 0), (x3, 0)],   # NOT x0 OR x2 OR x3
        [(x0, 0), (x1, 1), (x3, 1)],   # x0 OR NOT x1 OR NOT x3
        [(x0, 0), (x1, 0), (x2, 0)],   # x0 OR x1 OR x2
        [(x1, 0), (x2, 1), (x3, 1)],   # x1 OR NOT x2 OR NOT x3
    ]

    def wrap(cl):
        # For an all-ones-controlled mcx to fire exactly on the all-literals-false
        # assignment, we need each control qubit to be |1> in that assignment.
        # In the false assignment, qubit value = (1 - need_value_for_literal_false)?
        # Literal x_i false means qubit==0; literal NOT x_i false means qubit==1.
        # need==1 means literal-false requires qubit==1 -> no X.
        # need==0 means literal-false requires qubit==0 -> X wrap.
        return [q for (q, need) in cl if need == 0]

    # compute clause ancillas
    for k, cl in enumerate(clauses):
        qc.x(c[k])                      # default satisfied = 1
        w = wrap(cl)
        for q in w:
            qc.x(q)
        qc.mcx([q for (q, _) in cl], c[k])   # flip to 0 iff all literals false
        for q in w:
            qc.x(q)

    # AND of all clause ancillas into tgt
    qc.mcx(c, tgt)
    # phase
    qc.z(tgt)
    # uncompute AND
    qc.mcx(c, tgt)

    # uncompute clause ancillas (mirror)
    for k in reversed(range(len(clauses))):
        cl = clauses[k]
        w = wrap(cl)
        for q in w:
            qc.x(q)
        qc.mcx([q for (q, _) in cl], c[k])
        for q in w:
            qc.x(q)
        qc.x(c[k])
