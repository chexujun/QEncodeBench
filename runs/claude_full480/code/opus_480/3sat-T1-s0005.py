from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = ancilla_qubits[:4]
    t = ancilla_qubits[4]

    # Clause 1: (NOT x0 OR NOT x1 OR NOT x2) -> false iff x0=1,x1=1,x2=1
    # c0 = 1 iff clause satisfied. Clause unsatisfied only when all three true.
    # Compute clause-satisfied flag c0 = NOT(x0 AND x1 AND x2)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], t)     # t = x0 AND x1 AND x2 (using c[0] as temp for x0&x1)
    # wait: need c[0] to hold x0&x1 for uncompute; t holds AND of all three
    qc.x(t)                 # t = clause1 satisfied = NOT(all three)
    # uncompute c[0]
    qc.ccx(x0, x1, c[0])
    # now t = c1_sat, keep it. Rename: we'll accumulate satisfaction.

    # Clause 2: (x0 OR NOT x1 OR NOT x2) -> unsatisfied iff x0=0,x1=1,x2=1
    qc.x(x0)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[1])   # c[1] = x0'*x1*x2 = clause2 unsatisfied
    qc.ccx(x0, x1, c[0])     # uncompute c[0]
    qc.x(x0)
    qc.x(c[1])               # c[1] = clause2 satisfied

    # Clause 3: (NOT x0 OR x1 OR NOT x2) -> unsatisfied iff x0=1,x1=0,x2=1
    qc.x(x1)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[2])   # c[2] = clause3 unsatisfied
    qc.ccx(x0, x1, c[0])
    qc.x(x1)
    qc.x(c[2])               # c[2] = clause3 satisfied

    # Clause 4: (NOT x0 OR NOT x1 OR x2) -> unsatisfied iff x0=1,x1=1,x2=0
    qc.x(x2)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[3])   # c[3] = clause4 unsatisfied
    qc.ccx(x0, x1, c[0])
    qc.x(x2)
    qc.x(c[3])               # c[3] = clause4 satisfied

    # Now t=c1_sat, c[1]=c2_sat, c[2]=c3_sat, c[3]=c4_sat.
    # f = AND of all four. Apply phase -1 iff all four = 1 using mcp on t,c[1],c[2],c[3].
    qc.h(t)
    qc.mcx([c[1], c[2], c[3]], t)
    qc.h(t)

    # Uncompute everything in reverse order.
    # Uncompute clause4 flag c[3]
    qc.x(c[3])
    qc.x(x2)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[3])
    qc.ccx(x0, x1, c[0])
    qc.x(x2)

    # Uncompute clause3 flag c[2]
    qc.x(c[2])
    qc.x(x1)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[2])
    qc.ccx(x0, x1, c[0])
    qc.x(x1)

    # Uncompute clause2 flag c[1]
    qc.x(c[1])
    qc.x(x0)
    qc.ccx(x0, x1, c[0])
    qc.ccx(x2, c[0], c[1])
    qc.ccx(x0, x1, c[0])
    qc.x(x0)

    # Uncompute clause1 flag t
    qc.ccx(x0, x1, c[0])
    qc.x(t)
    qc.ccx(x2, c[0], t)
    qc.ccx(x0, x1, c[0])
