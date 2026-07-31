from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = ancilla_qubits[:4]
    t = ancilla_qubits[4]

    # Clause 1: (NOT x0 OR NOT x1 OR NOT x2) -> false only if x0=x1=x2=1
    # c0 = clause1 satisfied
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], t)      # t = x0 AND x1 AND x2 = clause1 unsatisfied
    qc.ccx(x2, c[0], c[0])   # placeholder-free: instead build directly below
    # Undo the temporary above cleanly by recomputing properly.
    # (Reset c[0] path)
    qc.ccx(x0, x1, c[0])     # uncompute c[0]
    qc.x(t)                  # c0-as-satisfied stored in t: t = NOT(x0&x1&x2)

    # Clause 2: (x0 OR x1 OR x2) satisfied unless all zero
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[1])   # c[1] = (NOT x0)(NOT x1)(NOT x2) = clause2 unsatisfied
    qc.ccx(x0, x1, c[0])     # uncompute c[0]
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.x(c[1])               # c[1] = clause2 satisfied

    # Clause 3: (x0 OR x1 OR NOT x2) unsatisfied iff x0=0,x1=0,x2=1
    qc.x(x0); qc.x(x1)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[2])   # c[2] = (NOT x0)(NOT x1)(x2) = clause3 unsatisfied
    qc.ccx(x0, x1, c[0])
    qc.x(x0); qc.x(x1)
    qc.x(c[2])               # c[2] = clause3 satisfied

    # Clause 4: (x0 OR NOT x1 OR NOT x2) unsatisfied iff x0=0,x1=1,x2=1
    qc.x(x0)
    qc.ccx(x1, x2, c[0])
    qc.ccx(x0, c[0], c[3])   # c[3] = (NOT x0)(x1)(x2) = clause4 unsatisfied
    qc.ccx(x1, x2, c[0])
    qc.x(x0)
    qc.x(c[3])               # c[3] = clause4 satisfied

    # AND all four clause-satisfied flags: t, c[1], c[2], c[3]
    qc.ccx(t, c[1], c[0])
    qc.ccx(c[2], c[3], c[0])   # wrong: reuse. Use separate accumulation.
    # Redo AND cleanly using controlled Z on accumulated ancilla.
    qc.ccx(c[2], c[3], c[0])   # uncompute the erroneous line above
    qc.ccx(t, c[1], c[0])      # uncompute first, c[0] back to 0

    # Proper AND: mcx of the four flags onto c[0], then Z, then uncompute
    qc.mcx([t, c[1], c[2], c[3]], c[0])
    qc.z(c[0])
    qc.mcx([t, c[1], c[2], c[3]], c[0])

    # Uncompute clause flags in reverse order
    # Clause 4 uncompute
    qc.x(c[3])
    qc.x(x0)
    qc.ccx(x1, x2, c[0])
    qc.ccx(x0, c[0], c[3])
    qc.ccx(x1, x2, c[0])
    qc.x(x0)

    # Clause 3 uncompute
    qc.x(c[2])
    qc.x(x0); qc.x(x1)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[2])
    qc.ccx(x0, x1, c[0])
    qc.x(x0); qc.x(x1)

    # Clause 2 uncompute
    qc.x(c[1])
    qc.x(x0); qc.x(x1); qc.x(x2)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[1])
    qc.ccx(x0, x1, c[0])
    qc.x(x0); qc.x(x1); qc.x(x2)

    # Clause 1 uncompute
    qc.x(t)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], t)
    qc.ccx(x0, x1, c[0])
