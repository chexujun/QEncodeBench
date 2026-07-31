from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 3), (1, 5), (2, 5), (4, 5)]
    violation = ancilla_qubits[0]
    
    def check_and_xor(u, v):
        """Check if vertices u and v have the same color and XOR result into violation."""
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        
        # For each possible same-color pair, check and XOR into violation
        # Colors: (b0, b1) -> color: (0,0)->0, (0,1)->2, (1,0)->1, (1,1)->0
        # Same color pairs: (0,0)=(0,0), (0,0)=(1,1), (0,1)=(0,1), (1,0)=(1,0), (1,1)=(0,0), (1,1)=(1,1)
        cases = [
            ([], [b0_u, b1_u, b0_v, b1_v]),        # (0,0,0,0)
            ([b0_v, b1_v], [b0_u, b1_u]),          # (0,0,1,1)
            ([b1_u, b1_v], [b0_u, b0_v]),          # (0,1,0,1)
            ([b0_u, b0_v], [b1_u, b1_v]),          # (1,0,1,0)
            ([b0_u, b1_u], [b0_v, b1_v]),          # (1,1,0,0)
            ([b0_u, b1_u, b0_v, b1_v], []),        # (1,1,1,1)
        ]
        
        for pos_controls, neg_qubits in cases:
            # Apply X to qubits that need to be 0
            for q in neg_qubits:
                qc.x(q)
            
            # Apply multi-controlled-X to flip violation
            all_controls = pos_controls + neg_qubits
            if len(all_controls) == 1:
                qc.cx(all_controls[0], violation)
            elif len(all_controls) == 2:
                qc.ccx(all_controls[0], all_controls[1], violation)
            else:
                qc.mcx(all_controls, violation)
            
            # Uncompute X gates
            for q in neg_qubits:
                qc.x(q)
    
    # Compute: accumulate monochromatic edges into violation flag
    for u, v in edges:
        check_and_xor(u, v)
    
    # Apply phase: -1 if valid (violation == 0)
    qc.x(violation)
    qc.z(violation)
    qc.x(violation)
    
    # Uncompute: reset violation flag to 0
    for u, v in reversed(edges):
        check_and_xor(u, v)
