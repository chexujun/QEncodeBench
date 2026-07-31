from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c0, c1, c2, c3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    phase = ancilla_qubits[4]

    # Clauses (a clause is FALSE only for one specific assignment of its 3 literals).
    # We compute clause_i = 1 iff clause satisfied, into ancilla c_i.
    # Approach: set ancilla to 1, then flip to 0 for the unique falsifying assignment.
    # Falsifying assignment makes every literal false.

    # Clause 0: (x0 OR NOT x1 OR NOT x2) -> false iff x0=0, x1=1, x2=1
    qc.x(c0)
    qc.x(x0)                       # so that "x0=0" becomes control-1
    qc.mcx([x0, x1, x2], c0)       # if x0=0,x1=1,x2=1 -> flip c0 to 0
    qc.x(x0)

    # Clause 1: (NOT x0 OR NOT x1 OR x2) -> false iff x0=1, x1=1, x2=0
    qc.x(c1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c1)
    qc.x(x2)

    # Clause 2: (NOT x0 OR x1 OR x2) -> false iff x0=1, x1=0, x2=0
    qc.x(c2)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x2)
    qc.x(x1)

    # Clause 3: (NOT x0 OR NOT x1 OR NOT x2) -> false iff x0=1, x1=1, x2=1
    qc.x(c3)
    qc.mcx([x0, x1, x2], c3)

    # f = AND of all clauses -> into phase ancilla
    qc.mcx([c0, c1, c2, c3], phase)
    qc.z(phase)
    qc.mcx([c0, c1, c2, c3], phase)

    # Uncompute clauses (mirror)
    qc.mcx([x0, x1, x2], c3)
    qc.x(c3)

    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x2)
    qc.x(x1)
    qc.x(c2)

    qc.x(x2)
    qc.mcx([x0, x1, x2], c1)
    qc.x(x2)
    qc.x(c1)

    qc.x(x0)
    qc.mcx([x0, x1, x2], c0)
    qc.x(x0)
    qc.x(c0)
