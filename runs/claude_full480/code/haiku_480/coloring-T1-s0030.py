from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (2, 3), (3, 4)]
    
    # For each edge, compute whether the constraint is violated (same color)
    # and store in ancilla_qubits[edge_idx]
    
    for edge_idx, (u, v) in enumerate(edges):
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        violation_anc = ancilla_qubits[edge_idx]
        temp_anc = ancilla_qubits[4]
        
        # Compute violation: 1 iff colors are same
        # Colors same iff: (b0_u == b1_u AND b0_v == b1_v) OR
        #                  (b0_u XOR b1_u AND b0_v XOR b1_v AND b0_u == b0_v)
        
        # Case 1: Both color 0 - b0_u == b1_u AND b0_v == b1_v
        qc.cx(b0_u, temp_anc)
        qc.cx(b1_u, temp_anc)
        qc.x(temp_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.x(violation_anc)
        qc.ccx(temp_anc, violation_anc, temp_anc)
        qc.x(violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.cx(b0_v, violation_anc)
        qc.x(temp_anc)
        qc.cx(b1_u, temp_anc)
        qc.cx(b0_u, temp_anc)
        
        # Case 2 & 3: Both color 1 or 2 - xor_u AND xor_v AND (b0_u == b0_v)
        qc.cx(b0_u, temp_anc)
        qc.cx(b1_u, temp_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.ccx(temp_anc, violation_anc, temp_anc)
        qc.cx(b0_u, violation_anc)
        qc.cx(b0_v, violation_anc)
        qc.x(violation_anc)
        qc.ccx(temp_anc, violation_anc, temp_anc)
        qc.x(violation_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b0_u, violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b1_u, temp_anc)
        qc.cx(b0_u, temp_anc)
    
    # OR all violations into temp_anc and apply phase if result is 0
    temp_anc = ancilla_qubits[4]
    
    for i in range(4):
        qc.cx(ancilla_qubits[i], temp_anc)
    
    qc.x(temp_anc)
    qc.p(math.pi, temp_anc)
    qc.x(temp_anc)
    
    for i in range(4):
        qc.cx(ancilla_qubits[i], temp_anc)
    
    # Uncompute violations
    for edge_idx in range(3, -1, -1):
        u, v = edges[edge_idx]
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        violation_anc = ancilla_qubits[edge_idx]
        temp_anc = ancilla_qubits[4]
        
        qc.cx(b0_u, temp_anc)
        qc.cx(b1_u, temp_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.x(violation_anc)
        qc.ccx(temp_anc, violation_anc, temp_anc)
        qc.x(violation_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b0_u, violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b1_u, temp_anc)
        qc.cx(b0_u, temp_anc)
        qc.cx(b0_u, temp_anc)
        qc.cx(b1_u, temp_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.ccx(temp_anc, violation_anc, temp_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b0_u, violation_anc)
        qc.cx(b1_v, violation_anc)
        qc.cx(b0_v, violation_anc)
        qc.cx(b1_u, temp_anc)
        qc.cx(b0_u, temp_anc)
