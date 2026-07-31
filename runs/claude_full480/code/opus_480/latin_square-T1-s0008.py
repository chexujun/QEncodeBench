from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: (0,1) and (2,2). Cell 0 -> qubits p0(low),p1(high); cell1 -> p2,p3.
    # Decoding surjective: 00->0, 01->1, 10->2, 11->0.
    #
    # Grid:
    #  1  A  0     A = cell0, at (row0,col1)
    #  2  0  1
    #  0  1  B     B = cell1, at (row2,col2)
    #
    # Constraints involving free cells:
    # Row0: {1, A, 0} distinct -> A != 1, A != 0 -> A must be 2.
    # Col1: {A, 0, 1} distinct -> A != 0, A != 1 -> A must be 2.
    # Row2: {0, 1, B} distinct -> B != 0, B != 1 -> B must be 2.
    # Col2: {0, 1, B} distinct -> B != 0, B != 1 -> B must be 2.
    # So f(x)=1 iff decode(A)==2 and decode(B)==2.
    # decode==2 only for code 10 (b0=0, b1=1). (11 decodes to 0, not 2.)
    # So need: p1==1 and p0==0 for cell0; p3==1 and p2==0 for cell1.

    p0, p1, p2, p3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a = ancilla_qubits

    # Compute cell0 == "value 2" predicate into a[0]: (NOT p0) AND p1
    qc.x(p0)
    qc.ccx(p0, p1, a[0])
    qc.x(p0)

    # Compute cell1 == "value 2" predicate into a[1]: (NOT p2) AND p3
    qc.x(p2)
    qc.ccx(p2, p3, a[1])
    qc.x(p2)

    # Phase flip iff a[0] AND a[1]
    qc.cz(a[0], a[1])

    # Uncompute
    qc.x(p2)
    qc.ccx(p2, p3, a[1])
    qc.x(p2)

    qc.x(p0)
    qc.ccx(p0, p1, a[0])
    qc.x(p0)
