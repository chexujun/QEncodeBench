import numpy as np
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (2, 3), (3, 4)]
    
    # Compute monochromatic status for each edge into ancilla_qubits[0:3]
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        mono = ancilla_qubits[i]
        
        # Case 0: (b0_u == b1_u) AND (b0_v == b1_v)
        # Combination 1: (00, 00)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_v)
        qc.x(b0_v)
        qc.x(b1_u)
        qc.x(b0_u)
        
        # Combination 2: (00, 11)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_u)
        qc.x(b0_u)
        
        # Combination 3: (11, 00)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_v)
        qc.x(b0_v)
        
        # Combination 4: (11, 11)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        
        # Case 1: (01, 01)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_v)
        qc.x(b1_u)
        
        # Case 2: (10, 10)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b0_v)
        qc.x(b0_u)
    
    # Apply phase if all edges are not monochromatic
    marker = ancilla_qubits[3]
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    
    # Flip ancillas to invert condition
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    
    # Set marker = 1 iff all three ancillas are 1 (originally 0)
    qc.x(marker)
    qc.mcx([a0, a1, a2], marker)
    
    # Apply Z phase
    qc.z(marker)
    
    # Uncompute marker
    qc.mcx([a0, a1, a2], marker)
    qc.x(marker)
    
    # Unflip ancillas
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    
    # Uncompute monochromatic flags (reverse order)
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        mono = ancilla_qubits[i]
        
        # Case 2: (10, 10)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b0_v)
        qc.x(b0_u)
        
        # Case 1: (01, 01)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_v)
        qc.x(b1_u)
        
        # Combination 4: (11, 11)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        
        # Combination 3: (11, 00)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_v)
        qc.x(b0_v)
        
        # Combination 2: (00, 11)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_u)
        qc.x(b0_u)
        
        # Combination 1: (00, 00)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], mono)
        qc.x(b1_v)
        qc.x(b0_v)
        qc.x(b1_u)
        qc.x(b0_u)
