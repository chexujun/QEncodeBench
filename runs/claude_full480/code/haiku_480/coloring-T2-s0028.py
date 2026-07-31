from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (2, 4), (3, 4)]
    
    def get_bits(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]
    
    # Ancillas: first 6 for violations, last 1 for result
    violation_ancs = ancilla_qubits[:6]
    result_anc = ancilla_qubits[6]
    
    # Compute violation flag for each edge
    # violation_anc[i] = 1 iff edge i has same color (violation)
    for edge_idx, (u, v) in enumerate(edges):
        u0, u1 = get_bits(u)
        v0, v1 = get_bits(v)
        v_anc = violation_ancs[edge_idx]
        
        # Same color occurs for 6 cases:
        # (u_code, v_code) in {(0,0), (0,3), (1,1), (2,2), (3,0), (3,3)}
        # In binary: (00,00), (00,11), (01,01), (10,10), (11,00), (11,11)
        
        same_color_cases = [
            (0, 0, 0, 0),  # (u1,u0,v1,v0)
            (0, 0, 1, 1),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
        ]
        
        for u1_val, u0_val, v1_val, v0_val in same_color_cases:
            # Apply controlled X to v_anc if this case matches
            # First, negate qubits that need to be |0> in the case
            qubits_to_negate = []
            if u1_val == 0:
                qubits_to_negate.append(u1)
            if u0_val == 0:
                qubits_to_negate.append(u0)
            if v1_val == 0:
                qubits_to_negate.append(v1)
            if v0_val == 0:
                qubits_to_negate.append(v0)
            
            # Apply X negations
            for q in qubits_to_negate:
                qc.x(q)
            
            # Multi-controlled X
            controls = [u1, u0, v1, v0]
            qc.mcx(controls, v_anc)
            
            # Uncompute X negations
            for q in qubits_to_negate:
                qc.x(q)
    
    # Check if all edges are satisfied (no violations)
    # Initialize result_anc to |1>
    qc.x(result_anc)
    
    # XOR each violation flag with result
    # result = 1 iff all violations are 0
    for v_anc in violation_ancs:
        qc.cx(v_anc, result_anc)
    
    # Apply Z gate when result_anc = |1>
    qc.z(result_anc)
    
    # Uncompute: reverse the XOR operations
    for v_anc in violation_ancs:
        qc.cx(v_anc, result_anc)
    qc.x(result_anc)
    
    # Uncompute violation flags in reverse
    for edge_idx in range(len(edges)-1, -1, -1):
        u, v = edges[edge_idx]
        u0, u1 = get_bits(u)
        v0, v1 = get_bits(v)
        v_anc = violation_ancs[edge_idx]
        
        same_color_cases = [
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
        ]
        
        # Uncompute in reverse order
        for u1_val, u0_val, v1_val, v0_val in reversed(same_color_cases):
            qubits_to_negate = []
            if u1_val == 0:
                qubits_to_negate.append(u1)
            if u0_val == 0:
                qubits_to_negate.append(u0)
            if v1_val == 0:
                qubits_to_negate.append(v1)
            if v0_val == 0:
                qubits_to_negate.append(v0)
            
            for q in qubits_to_negate:
                qc.x(q)
            
            controls = [u1, u0, v1, v0]
            qc.mcx(controls, v_anc)
            
            for q in qubits_to_negate:
                qc.x(q)
