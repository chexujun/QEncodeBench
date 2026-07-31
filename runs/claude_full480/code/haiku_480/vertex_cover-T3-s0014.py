from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,4), (1,3), (1,4), (2,4), (3,4), (3,5)]
    
    # Ancilla assignments
    any_uncovered = ancilla_qubits[0]        # 1 if any edge is uncovered
    popcount_gt4 = ancilla_qubits[1]         # 1 if popcount > 4
    phase_qubit = ancilla_qubits[2]          # 1 if valid (apply phase)
    temp = ancilla_qubits[3]                 # temporary for edge computation
    popcount = ancilla_qubits[4:7]           # 3-bit popcount accumulator
    
    # ===== COMPUTE PHASE =====
    
    # 1. Check if all edges are covered
    for i, j in edges:
        # Compute: edge_uncovered = (x[i] == 0) AND (x[j] == 0)
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
        
        # Accumulate: any_uncovered |= temp using controlled flip
        qc.cx(temp, any_uncovered)
        
        # Reset temp for next iteration
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
    
    # 2. Compute popcount and check if > 4
    # Binary addition for each problem qubit
    for k in range(6):
        qc.cx(problem_qubits[k], popcount[0])
        qc.toffoli(problem_qubits[k], popcount[0], popcount[1])
        qc.cx(problem_qubits[k], popcount[0])
        
        qc.cx(popcount[1], popcount[2])
        qc.toffoli(popcount[1], popcount[2], ancilla_qubits[7])
        qc.cx(popcount[1], popcount[2])
        
        if k < 5:
            qc.cx(ancilla_qubits[7], popcount[1])
            # Reset ancilla_qubits[7]
            qc.toffoli(popcount[1], popcount[2], ancilla_qubits[7])
    
    # Check if popcount > 4: set popcount_gt4 if popcount_bits represent >= 5
    # popcount >= 5 iff (popcount[2]==1) OR (popcount[1]==1 AND popcount[0]==1)
    qc.ccx(popcount[1], popcount[0], temp)
    qc.cx(temp, popcount_gt4)
    qc.cx(popcount[2], popcount_gt4)
    qc.ccx(popcount[1], popcount[0], temp)
    
    # 3. Compute final condition: phase_qubit = NOT(any_uncovered) AND NOT(popcount_gt4)
    qc.x(any_uncovered)
    qc.x(popcount_gt4)
    qc.ccx(any_uncovered, popcount_gt4, phase_qubit)
    qc.x(popcount_gt4)
    qc.x(any_uncovered)
    
    # 4. Apply phase
    qc.z(phase_qubit)
    
    # ===== UNCOMPUTE =====
    
    # Uncompute final condition
    qc.x(any_uncovered)
    qc.x(popcount_gt4)
    qc.ccx(any_uncovered, popcount_gt4, phase_qubit)
    qc.x(popcount_gt4)
    qc.x(any_uncovered)
    
    # Uncompute popcount logic (reverse order)
    for k in range(5, -1, -1):
        if k < 5:
            qc.toffoli(popcount[1], popcount[2], ancilla_qubits[7])
            qc.cx(ancilla_qubits[7], popcount[1])
        
        qc.toffoli(popcount[1], popcount[2], ancilla_qubits[7])
        qc.cx(popcount[1], popcount[2])
        
        qc.cx(problem_qubits[k], popcount[0])
        qc.toffoli(problem_qubits[k], popcount[0], popcount[1])
        qc.cx(problem_qubits[k], popcount[0])
    
    # Uncompute edge checks (reverse order)
    for i, j in reversed(edges):
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
        
        qc.cx(temp, any_uncovered)
        
        qc.x(problem_qubits[i])
        qc.x(problem_qubits[j])
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        qc.x(problem_qubits[j])
        qc.x(problem_qubits[i])
