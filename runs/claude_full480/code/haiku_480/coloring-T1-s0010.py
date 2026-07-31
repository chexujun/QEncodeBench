from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 2), (1, 3)]
    edge_check = ancilla_qubits[:3]
    phase_qubit = ancilla_qubits[3]
    
    # Compute edge_check bits: for each edge, mark 1 iff colors differ
    for edge_idx, (u, v) in enumerate(edges):
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u+1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v+1]
        
        a = edge_check[edge_idx]
        
        # Compute: a = (b1_u XOR b1_v) XOR (b0_u XOR b0_v)
        # This is 1 iff decode(u) != decode(v), where decode maps codes 0,1,2,3 -> colors 0,1,2,0
        qc.cx(u_b1, a)
        qc.cx(v_b1, a)
        qc.cx(u_b0, a)
        qc.cx(v_b0, a)
    
    # Prepare phase_qubit in state |1⟩
    qc.x(phase_qubit)
    
    # Apply multi-controlled phase: gate applies phase -1 iff all edge_check bits are |1⟩
    qc.mcp(np.pi, edge_check, phase_qubit)
    
    # Flip phase_qubit back to |0⟩ (with accumulated phase if all constraints met)
    qc.x(phase_qubit)
    
    # Uncompute edge_check bits (reverse order)
    for edge_idx, (u, v) in enumerate(edges):
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u+1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v+1]
        
        a = edge_check[edge_idx]
        
        qc.cx(v_b0, a)
        qc.cx(u_b0, a)
        qc.cx(v_b1, a)
        qc.cx(u_b1, a)
