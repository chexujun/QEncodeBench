from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for each free cell
    # Free cell i uses qubits problem_qubits[2i] (b0_i, low bit) and problem_qubits[2i+1] (b1_i, high bit)
    # Decoding: 00->0, 01->1, 10->2, 11->0
    # We need all three cells to decode to value 2, which requires b0_i=0 and b1_i=1
    # This is equivalent to: NOT b0_i AND b1_i for each cell i
    
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]
    
    # Use ancilla qubits for computation
    cond0 = ancilla_qubits[0]  # Condition for cell 0: NOT b0_0 AND b1_0
    cond1 = ancilla_qubits[1]  # Condition for cell 1: NOT b0_1 AND b1_1
    cond2 = ancilla_qubits[2]  # Condition for cell 2: NOT b0_2 AND b1_2
    temp = ancilla_qubits[3]   # Temporary for AND accumulation
    result = ancilla_qubits[4] # Final AND result
    
    # COMPUTE PHASE: Calculate the three conditions and their AND
    
    # Cell 0: cond0 = NOT b0_0 AND b1_0
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, cond0)
    qc.x(b0_0)
    
    # Cell 1: cond1 = NOT b0_1 AND b1_1
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, cond1)
    qc.x(b0_1)
    
    # Cell 2: cond2 = NOT b0_2 AND b1_2
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, cond2)
    qc.x(b0_2)
    
    # Compute result = cond0 AND cond1 AND cond2
    qc.ccx(cond0, cond1, temp)
    qc.ccx(temp, cond2, result)
    
    # APPLY PHASE: Apply phase -1 if result is 1 (all conditions met)
    qc.z(result)
    
    # UNCOMPUTE: Reverse all operations to restore ancillas to |0>
    
    # Undo the AND operations
    qc.ccx(temp, cond2, result)
    qc.ccx(cond0, cond1, temp)
    
    # Undo the individual condition calculations
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, cond2)
    qc.x(b0_2)
    
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, cond1)
    qc.x(b0_1)
    
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, cond0)
    qc.x(b0_0)
