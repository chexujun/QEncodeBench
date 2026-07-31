from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits (2 bits per free cell, value = (b0 + 2*b1) mod 3)
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # Free cell 0 at (0,0)
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]  # Free cell 1 at (1,2)
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]  # Free cell 2 at (2,1)
    
    # Ancilla qubits for computing constraints
    const0 = ancilla_qubits[0]    # Constraint: val0 = 1
    const1 = ancilla_qubits[1]    # Constraint: val1 = 0
    const2 = ancilla_qubits[2]    # Constraint: val2 = 2
    and_temp = ancilla_qubits[3]  # Temporary for (const0 AND const1)
    result = ancilla_qubits[4]    # Final result (const0 AND const1 AND const2)
    
    # COMPUTE PHASE
    
    # Compute const0: val0 = 1 iff b0_0 = 1 AND b1_0 = 0
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, const0)
    qc.x(b1_0)
    
    # Compute const1: val1 = 0 iff (b0_1, b1_1) in {(0,0), (1,1)}
    # Equivalently: NOT (b0_1 XOR b1_1)
    qc.cx(b0_1, const1)
    qc.cx(b1_1, const1)
    qc.x(const1)
    
    # Compute const2: val2 = 2 iff b0_2 = 0 AND b1_2 = 1
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, const2)
    qc.x(b0_2)
    
    # Compute result = const0 AND const1 AND const2
    qc.ccx(const0, const1, and_temp)
    qc.ccx(and_temp, const2, result)
    
    # APPLY PHASE
    qc.z(result)
    
    # UNCOMPUTE PHASE
    
    # Uncompute result
    qc.ccx(and_temp, const2, result)
    qc.ccx(const0, const1, and_temp)
    
    # Uncompute const2
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, const2)
    qc.x(b0_2)
    
    # Uncompute const1
    qc.x(const1)
    qc.cx(b1_1, const1)
    qc.cx(b0_1, const1)
    
    # Uncompute const0
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, const0)
    qc.x(b1_0)
