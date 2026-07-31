from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: (0,0) uses problem_qubits[0]=b0, problem_qubits[1]=b1
    #             (0,1) uses problem_qubits[2]=b0, problem_qubits[3]=b1
    # Decode: 00->0, 01->1, 10->2, 11->0
    #
    # Grid:
    #   c00 c01  2
    #    1   2   0
    #    2   0   1
    #
    # Column constraints:
    #   col0 has {1,2} given -> c00 must be 0
    #   col1 has {2,0} given -> c01 must be 1
    #   col2 fixed = 2,0,1 ok
    # Row0 constraint: {c00, c01, 2} all different -> needs {0,1,2}, so
    #   {c00,c01} = {0,1}. Combined with col constraints c00=0, c01=1.
    #
    # So f(x)=1 iff c00==0 AND c01==1.
    # c00==0 : decode value 0 <- codes 00 or 11 -> (b0==b1) for cell0
    # c01==1 : decode value 1 <- code 01 -> b0==1, b1==0 for cell1

    b0_0 = problem_qubits[0]
    b1_0 = problem_qubits[1]
    b0_1 = problem_qubits[2]
    b1_1 = problem_qubits[3]

    a0 = ancilla_qubits[0]  # holds (c00 == 0)
    a1 = ancilla_qubits[1]  # holds (c01 == 1)

    # Compute a0 = 1 iff b0_0 == b1_0  (value 0: codes 00 or 11)
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    qc.x(a0)  # a0 = NOT(b0_0 XOR b1_0) = (b0_0 == b1_0)

    # Compute a1 = 1 iff (b0_1 == 1 and b1_1 == 0)  (code 01 -> value 1)
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)

    # Phase: -1 iff a0 AND a1
    qc.cz(a0, a1)

    # Uncompute a1
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)

    # Uncompute a0
    qc.x(a0)
    qc.cx(b1_0, a0)
    qc.cx(b0_0, a0)
