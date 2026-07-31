from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], 
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubit indices
    x0, x1 = problem_qubits[0], problem_qubits[1]
    x2, x3 = problem_qubits[2], problem_qubits[3]
    
    # Allocate ancilla qubits
    a_temp = ancilla_qubits[0]
    a_const1 = ancilla_qubits[1]
    a_const2 = ancilla_qubits[2]
    a_result = ancilla_qubits[3]
    
    # Compute constraint 1: x0 AND NOT x1
    # Cell (2,1) must equal 1, which requires code 01
    qc.cx(x1, a_temp)
    qc.x(a_temp)
    qc.ccx(x0, a_temp, a_const1)
    
    # Compute constraint 2: x2 == x3
    # Cell (2,2) must equal 0, which requires code 00 or 11 (x2 XNOR x3)
    qc.x(a_const2)
    qc.cx(x2, a_const2)
    qc.cx(x3, a_const2)
    
    # AND the constraints
    qc.ccx(a_const1, a_const2, a_result)
    
    # Apply phase flip
    qc.z(a_result)
    
    # Uncompute (reverse order)
    qc.ccx(a_const1, a_const2, a_result)
    
    qc.cx(x3, a_const2)
    qc.cx(x2, a_const2)
    qc.x(a_const2)
    
    qc.ccx(x0, a_temp, a_const1)
    qc.x(a_temp)
    qc.cx(x1, a_temp)
