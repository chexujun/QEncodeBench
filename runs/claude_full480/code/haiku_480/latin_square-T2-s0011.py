from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract qubits for each free cell
    # Free cell j uses problem_qubits[2j] (low bit) and problem_qubits[2j+1] (high bit)
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]
    
    # Use first ancilla for computing the constraint
    anc = ancilla_qubits[0]
    
    # For a valid 3x3 Latin square, all free cells must decode to value 1
    # Given the grid, row and column constraints force:
    # - Free cell 0 (row 0, col 2): must be 1 (row has 2,0)
    # - Free cell 1 (row 1, col 1): must be 1 (row has 0,2)
    # - Free cell 2 (row 2, col 0): must be 1 (row has 2,0)
    # This requires all codes to be 01 (binary), since decode(01) = 1
    # Constraint: (b0_0=1 AND b1_0=0) AND (b0_1=1 AND b1_1=0) AND (b0_2=1 AND b1_2=0)
    
    # Flip high bits to convert NOT b1_i constraints to direct controls
    qc.x(b1_0)
    qc.x(b1_1)
    qc.x(b1_2)
    
    # Compute: use multi-controlled X to compute AND of all 6 bits into ancilla
    controls = [b0_0, b0_1, b0_2, b1_0, b1_1, b1_2]
    qc.mcx(controls, anc)
    
    # Apply phase: Z gate on ancilla marks states where constraint is satisfied
    qc.z(anc)
    
    # Uncompute: reverse the MCX to restore ancilla to |0>
    qc.mcx(controls, anc)
    
    # Restore high bits to original values
    qc.x(b1_0)
    qc.x(b1_1)
    qc.x(b1_2)
