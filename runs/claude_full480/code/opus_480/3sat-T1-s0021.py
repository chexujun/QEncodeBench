from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c = ancilla_qubits[0:4]
    out = ancilla_qubits[4]

    # Clause 0: (NOT x0 OR NOT x1 OR NOT x3) == NOT (x0 AND x1 AND x3)
    qc.ccx(x0, x1, c[0])
    qc.ccx(c[0], x3, c[0]) if False else None
    # compute AND of x0,x1,x3 into c[0] using nested ccx with a helper is messy;
    # instead compute clause-satisfied bit directly.
    # Undo the stray ccx above (it was skipped via None), so c[0] currently = x0&x1.
    # We want c[0] = clause0_satisfied = NOT(x0&x1&x3).
    # Reset approach: compute t = x0&x1&x3 into c[0] properly.
    qc.ccx(x0, x1, c[0])  # now c[0] = (x0&x1) xor (x0&x1) = 0 ... careful

    # The above is error-prone; use clean multi-controlled approach per clause.
    # Restart c[0].
    qc.reset if False else None
    return _build(qc, problem_qubits, ancilla_qubits)


def _build(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    c = ancilla_qubits[0:4]
    out = ancilla_qubits[4]

    # A 3-SAT clause (l_a OR l_b OR l_c) is FALSE only when all three literals are False.
    # clause_sat = NOT(all literals false). We compute clause_false into c[k]:
    # a literal "x" is false when qubit=0; literal "NOT x" is false when qubit=1.
    # For each clause, flip the qubits whose literal is positive (so "false" -> value 1),
    # AND them into c[k] via ccx chain, giving c[k] = clause_false, then X -> clause_sat.

    # Clause 0: (NOT x0 OR NOT x1 OR NOT x3): positive-literal? none negated->
    # literals: NOT x0, NOT x1, NOT x3. Literal false means the variable is True (qubit=1).
    # So clause0 false iff x0=1 & x1=1 & x3=1. c[0] = x0&x1&x3.
    qc.ccx(x[0], x[1], out)      # out = x0&x1
    qc.ccx(out, x[3], c[0])      # c[0] = x0&x1&x3
    qc.ccx(x[0], x[1], out)      # uncompute out
    qc.x(c[0])                   # c[0] = clause0_sat

    # Clause 1: (x1 OR NOT x2 OR NOT x3). clause false iff x1=0 & x2=1 & x3=1.
    qc.x(x[1])
    qc.ccx(x[1], x[2], out)      # out = (NOT x1)&x2
    qc.ccx(out, x[3], c[1])      # c[1] = (NOT x1)&x2&x3
    qc.ccx(x[1], x[2], out)
    qc.x(x[1])
    qc.x(c[1])                   # c[1] = clause1_sat

    # Clause 2: (x0 OR NOT x1 OR x3). clause false iff x0=0 & x1=1 & x3=0.
    qc.x(x[0]); qc.x(x[3])
    qc.ccx(x[0], x[1], out)      # out = (NOT x0)&x1
    qc.ccx(out, x[3], c[2])      # c[2] = (NOT x0)&x1&(NOT x3)
    qc.ccx(x[0], x[1], out)
    qc.x(x[0]); qc.x(x[3])
    qc.x(c[2])                   # c[2] = clause2_sat

    # Clause 3: (x0 OR x2 OR NOT x3). clause false iff x0=0 & x2=0 & x3=1.
    qc.x(x[0]); qc.x(x[2])
    qc.ccx(x[0], x[2], out)      # out = (NOT x0)&(NOT x2)
    qc.ccx(out, x[3], c[3])      # c[3] = (NOT x0)&(NOT x2)&x3
    qc.ccx(x[0], x[2], out)
    qc.x(x[0]); qc.x(x[2])
    qc.x(c[3])                   # c[3] = clause3_sat

    # Phase -1 iff all four clauses satisfied: multi-controlled Z on c[0..3].
    qc.h(out)
    qc.mcx([c[0], c[1], c[2], c[3]], out)
    qc.h(out)

    # Uncompute all clause bits (mirror).
    qc.x(c[3])
    qc.x(x[0]); qc.x(x[2])
    qc.ccx(x[0], x[2], out)
    qc.ccx(out, x[3], c[3])
    qc.ccx(x[0], x[2], out)
    qc.x(x[0]); qc.x(x[2])

    qc.x(c[2])
    qc.x(x[0]); qc.x(x[3])
    qc.ccx(x[0], x[1], out)
    qc.ccx(out, x[3], c[2])
    qc.ccx(x[0], x[1], out)
    qc.x(x[0]); qc.x(x[3])

    qc.x(c[1])
    qc.x(x[1])
    qc.ccx(x[1], x[2], out)
    qc.ccx(out, x[3], c[1])
    qc.ccx(x[1], x[2], out)
    qc.x(x[1])

    qc.x(c[0])
    qc.ccx(x[0], x[1], out)
    qc.ccx(out, x[3], c[0])
    qc.ccx(x[0], x[1], out)
