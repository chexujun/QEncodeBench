from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (2, 4)]
    
    # Use ancillas[0:5] for same_color of each edge
    same_color_ancillas = ancilla_qubits[:5]
    
    # Step 1: Compute same_color for each edge
    # same_color[i] = 1 iff vertices of edge i have the same decoded color
    for edge_idx, (u, v) in enumerate(edges):
        u_low, u_high = problem_qubits[2*u], problem_qubits[2*u+1]
        v_low, v_high = problem_qubits[2*v], problem_qubits[2*v+1]
        ancilla = same_color_ancillas[edge_idx]
        
        # Check all 6 valid combinations where colors match:
        # (0,0,0,0), (0,0,1,1), (1,1,0,0), (1,1,1,1): both decode to color 0
        # (1,0,1,0): both decode to color 1
        # (0,1,0,1): both decode to color 2
        
        # Combination 1: (0,0,0,0)
        qc.x(u_low)
        qc.x(u_high)
        qc.x(v_low)
        qc.x(v_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_low)
        qc.x(u_high)
        qc.x(v_low)
        qc.x(v_high)
        
        # Combination 2: (0,0,1,1)
        qc.x(u_low)
        qc.x(u_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_low)
        qc.x(u_high)
        
        # Combination 3: (0,1,0,1)
        qc.x(u_low)
        qc.x(v_low)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_low)
        qc.x(v_low)
        
        # Combination 4: (1,0,1,0)
        qc.x(u_high)
        qc.x(v_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_high)
        qc.x(v_high)
        
        # Combination 5: (1,1,0,0)
        qc.x(v_low)
        qc.x(v_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(v_low)
        qc.x(v_high)
        
        # Combination 6: (1,1,1,1)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
    
    # Step 2: Apply phase -1 when all edges have different colors
    # This happens when all same_color values are 0
    # Flip ancillas to compute NOT same_color
    for ancilla in same_color_ancillas:
        qc.x(ancilla)
    
    # Apply multi-controlled Z gate (via multi-controlled P gate with theta=pi)
    # Applies -1 phase when all NOT same_color are 1 (i.e., all same_color are 0)
    qc.mcp(np.pi, same_color_ancillas[:4], same_color_ancillas[4])
    
    # Flip ancillas back
    for ancilla in same_color_ancillas:
        qc.x(ancilla)
    
    # Step 3: Uncompute same_color for each edge
    for edge_idx, (u, v) in enumerate(edges):
        u_low, u_high = problem_qubits[2*u], problem_qubits[2*u+1]
        v_low, v_high = problem_qubits[2*v], problem_qubits[2*v+1]
        ancilla = same_color_ancillas[edge_idx]
        
        # Mirror of compute (reverse order of combinations)
        
        # Combination 6: (1,1,1,1)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        
        # Combination 5: (1,1,0,0)
        qc.x(v_low)
        qc.x(v_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(v_low)
        qc.x(v_high)
        
        # Combination 4: (1,0,1,0)
        qc.x(u_high)
        qc.x(v_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_high)
        qc.x(v_high)
        
        # Combination 3: (0,1,0,1)
        qc.x(u_low)
        qc.x(v_low)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_low)
        qc.x(v_low)
        
        # Combination 2: (0,0,1,1)
        qc.x(u_low)
        qc.x(u_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_low)
        qc.x(u_high)
        
        # Combination 1: (0,0,0,0)
        qc.x(u_low)
        qc.x(u_high)
        qc.x(v_low)
        qc.x(v_high)
        qc.mcx([u_low, u_high, v_low, v_high], ancilla)
        qc.x(u_low)
        qc.x(u_high)
        qc.x(v_low)
        qc.x(v_high)
