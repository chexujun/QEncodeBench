from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 3), (3, 4)]
    
    # For each (u_b1, u_b0, v_b1, v_b0), determine if colors differ
    # Colors: (b1,b0) -> (0,0)->0, (0,1)->1, (1,0)->2, (1,1)->0
    # Colors differ in these 10 cases:
    colors_different_cases = [
        (0, 0, 0, 1), (0, 0, 1, 0),
        (0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 1, 1),
        (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 1),
        (1, 1, 0, 1), (1, 1, 1, 0),
    ]
    
    ancilla_edge = ancilla_qubits[0]
    ancilla_acc = ancilla_qubits[1]
    
    # Forward pass: compute AND of all edge_satisfied values
    for idx, (u, v) in enumerate(edges):
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u + 1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v + 1]
        
        # Compute edge_satisfied into ancilla_edge
        for u_b1_val, u_b0_val, v_b1_val, v_b0_val in colors_different_cases:
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
            
            qc.mcx([u_b1, u_b0, v_b1, v_b0], ancilla_edge)
            
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
        
        # Update ancilla_acc
        if idx == 0:
            qc.cx(ancilla_edge, ancilla_acc)
        else:
            qc.x(ancilla_edge)
            qc.ccx(ancilla_acc, ancilla_edge, ancilla_acc)
            qc.x(ancilla_edge)
        
        # Uncompute ancilla_edge
        for u_b1_val, u_b0_val, v_b1_val, v_b0_val in reversed(colors_different_cases):
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
            
            qc.mcx([u_b1, u_b0, v_b1, v_b0], ancilla_edge)
            
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
    
    # Apply phase
    qc.p(np.pi, ancilla_acc)
    
    # Backward pass: reverse the forward pass
    for idx, (u, v) in enumerate(reversed(edges)):
        idx = len(edges) - 1 - idx
        
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u + 1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v + 1]
        
        # Compute edge_satisfied into ancilla_edge
        for u_b1_val, u_b0_val, v_b1_val, v_b0_val in colors_different_cases:
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
            
            qc.mcx([u_b1, u_b0, v_b1, v_b0], ancilla_edge)
            
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
        
        # Reverse the update to ancilla_acc
        if idx == 0:
            qc.cx(ancilla_edge, ancilla_acc)
        else:
            qc.x(ancilla_edge)
            qc.ccx(ancilla_acc, ancilla_edge, ancilla_acc)
            qc.x(ancilla_edge)
        
        # Uncompute ancilla_edge
        for u_b1_val, u_b0_val, v_b1_val, v_b0_val in reversed(colors_different_cases):
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
            
            qc.mcx([u_b1, u_b0, v_b1, v_b0], ancilla_edge)
            
            if u_b1_val == 0:
                qc.x(u_b1)
            if u_b0_val == 0:
                qc.x(u_b0)
            if v_b1_val == 0:
                qc.x(v_b1)
            if v_b0_val == 0:
                qc.x(v_b0)
