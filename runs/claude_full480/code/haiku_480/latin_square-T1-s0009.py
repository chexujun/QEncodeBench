from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The only valid Latin square completion requires both free cells to have value 1.
    # Free cell 0 at (0,0): needs value 1 (encoding 01: b0=1, b1=0)
    # Free cell 1 at (2,1): needs value 1 (encoding 01: b0=1, b1=0)
    
    anc_0 = ancilla_qubits[0]
    anc_1 = ancilla_qubits[1]
    anc_result = ancilla_qubits[2]
    
    # Compute anc_0 = 1 iff (problem_qubits[0]=1 AND problem_qubits[1]=0)
    qc.x(problem_qubits[1])
    qc.ccx(problem_qubits[0], problem_qubits[1], anc_0)
    qc.x(problem_qubits[1])
    
    # Compute anc_1 = 1 iff (problem_qubits[2]=1 AND problem_qubits[3]=0)
    qc.x(problem_qubits[3])
    qc.ccx(problem_qubits[2], problem_qubits[3], anc_1)
    qc.x(problem_qubits[3])
    
    # Compute anc_result = anc_0 AND anc_1
    qc.ccx(anc_0, anc_1, anc_result)
    
    # Apply phase flip to marked states
    qc.z(anc_result)
    
    # Uncompute in reverse order
    qc.ccx(anc_0, anc_1, anc_result)
    qc.x(problem_qubits[3])
    qc.ccx(problem_qubits[2], problem_qubits[3], anc_1)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[1])
    qc.ccx(problem_qubits[0], problem_qubits[1], anc_0)
    qc.x(problem_qubits[1])
