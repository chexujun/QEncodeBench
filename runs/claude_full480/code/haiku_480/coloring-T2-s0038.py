from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]
    
    # Monochromatic cases: (b0_u, b1_u, b0_v, b1_v)
    # A state is monochromatic when both vertices have the same decoded color.
    # Decoding: 00→0, 01→1, 10→2, 11→0
    # Same color iff: both in {00,11} (color 0), or both 01 (color 1), or both 10 (color 2)
    mono_cases = [
        (0,0,0,0),  # both color 0
        (0,0,1,1),  # both color 0
        (0,1,0,1),  # both color 1
        (1,0,1,0),  # both color 2
        (1,1,0,0),  # both color 0
        (1,1,1,1),  # both color 0
    ]
    
    workspace = ancilla_qubits[0]
    other_ancillas = ancilla_qubits[1:]
    
    # Compute phase: workspace = 1 iff ALL edges properly colored (no monochromatic edge)
    # Initialize workspace to 1
    qc.x(workspace)
    
    # For each edge and each monochromatic case, flip workspace if matched
    for u, v in edges:
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u+1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v+1]
        
        for val_b0_u, val_b1_u, val_b0_v, val_b1_v in mono_cases:
            controls = []
            
            # Prepare controls: apply X to qubits that should be 0
            if val_b0_u == 0:
                qc.x(b0_u)
            controls.append(b0_u)
            
            if val_b1_u == 0:
                qc.x(b1_u)
            controls.append(b1_u)
            
            if val_b0_v == 0:
                qc.x(b0_v)
            controls.append(b0_v)
            
            if val_b1_v == 0:
                qc.x(b1_v)
            controls.append(b1_v)
            
            # Apply multi-controlled X to flip workspace
            if len(controls) == 1:
                qc.cx(controls[0], workspace)
            elif len(controls) == 2:
                qc.ccx(controls[0], controls[1], workspace)
            else:
                qc.mcx(controls, workspace, other_ancillas)
            
            # Uncompute X gates
            if val_b0_u == 0:
                qc.x(b0_u)
            if val_b1_u == 0:
                qc.x(b1_u)
            if val_b0_v == 0:
                qc.x(b0_v)
            if val_b1_v == 0:
                qc.x(b1_v)
    
    # Apply phase: -1 if workspace = 1 (i.e., all edges properly colored)
    qc.z(workspace)
    
    # Uncompute: reverse all flips
    for u, v in reversed(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u+1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v+1]
        
        for val_b0_u, val_b1_u, val_b0_v, val_b1_v in reversed(mono_cases):
            controls = []
            
            if val_b0_u == 0:
                qc.x(b0_u)
            controls.append(b0_u)
            
            if val_b1_u == 0:
                qc.x(b1_u)
            controls.append(b1_u)
            
            if val_b0_v == 0:
                qc.x(b0_v)
            controls.append(b0_v)
            
            if val_b1_v == 0:
                qc.x(b1_v)
            controls.append(b1_v)
            
            if len(controls) == 1:
                qc.cx(controls[0], workspace)
            elif len(controls) == 2:
                qc.ccx(controls[0], controls[1], workspace)
            else:
                qc.mcx(controls, workspace, other_ancillas)
            
            if val_b0_u == 0:
                qc.x(b0_u)
            if val_b1_u == 0:
                qc.x(b1_u)
            if val_b0_v == 0:
                qc.x(b0_v)
            if val_b1_v == 0:
                qc.x(b1_v)
    
    # Restore workspace to |0>
    qc.x(workspace)
