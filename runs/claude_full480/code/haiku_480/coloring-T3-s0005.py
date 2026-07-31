from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 2), (1, 3), (1, 5), (2, 4), (2, 5), (3, 4)]
    
    violation = ancilla_qubits[0]
    temp1 = ancilla_qubits[1]
    temp2 = ancilla_qubits[2]
    temp3 = ancilla_qubits[3]
    
    # Compute: violation = 1 if any edge is monochromatic (colors same)
    for u, v in edges:
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        # Check if colors equal: (identical codes) OR (both map to color 0)
        # Identical: (b0_u==b0_v AND b1_u==b1_v)
        qc.cx(b0_u, temp1)
        qc.cx(b0_v, temp1)
        qc.x(temp1)
        
        qc.cx(b1_u, temp2)
        qc.cx(b1_v, temp2)
        qc.x(temp2)
        
        qc.ccx(temp1, temp2, temp3)
        
        # Uncompute temp1, temp2
        qc.x(temp2)
        qc.cx(b1_v, temp2)
        qc.cx(b1_u, temp2)
        qc.x(temp1)
        qc.cx(b0_v, temp1)
        qc.cx(b0_u, temp1)
        
        # Both map to color 0: (b0_u==b1_u AND b0_v==b1_v)
        qc.cx(b0_u, temp1)
        qc.cx(b1_u, temp1)
        qc.x(temp1)
        
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        qc.x(temp2)
        
        # OR temp3 with (temp1 AND temp2)
        qc.cx(temp1, temp3)
        qc.ccx(temp1, temp2, temp1)
        qc.cx(temp1, temp3)
        qc.ccx(temp1, temp2, temp1)
        
        # Uncompute temp1, temp2
        qc.x(temp2)
        qc.cx(b1_v, temp2)
        qc.cx(b0_v, temp2)
        qc.x(temp1)
        qc.cx(b1_u, temp1)
        qc.cx(b0_u, temp1)
        
        # OR temp3 into violation
        qc.cx(temp3, violation)
        qc.ccx(temp3, violation, temp1)
        qc.cx(temp1, violation)
        qc.ccx(temp3, violation, temp1)
        
        qc.cx(temp3, temp3)  # Reset temp3
    
    # Apply phase if no violations (violation==0)
    qc.x(violation)
    qc.z(violation)
    qc.x(violation)
    
    # Uncompute in reverse
    for u, v in reversed(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        # Un-OR temp3 from violation
        qc.cx(temp3, temp3)
        qc.ccx(temp3, violation, temp1)
        qc.cx(temp1, violation)
        qc.ccx(temp3, violation, temp1)
        qc.cx(temp3, violation)
        
        # Compute and uncompute color conditions
        qc.cx(b0_u, temp1)
        qc.cx(b1_u, temp1)
        qc.x(temp1)
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        qc.x(temp2)
        
        qc.cx(temp1, temp3)
        qc.ccx(temp1, temp2, temp1)
        qc.cx(temp1, temp3)
        qc.ccx(temp1, temp2, temp1)
        
        qc.x(temp2)
        qc.cx(b1_v, temp2)
        qc.cx(b0_v, temp2)
        qc.x(temp1)
        qc.cx(b1_u, temp1)
        qc.cx(b0_u, temp1)
        
        qc.cx(b0_u, temp1)
        qc.cx(b0_v, temp1)
        qc.x(temp1)
        qc.cx(b1_u, temp2)
        qc.cx(b1_v, temp2)
        qc.x(temp2)
        
        qc.ccx(temp1, temp2, temp3)
        
        qc.x(temp2)
        qc.cx(b1_v, temp2)
        qc.cx(b1_u, temp2)
        qc.x(temp1)
        qc.cx(b0_v, temp1)
        qc.cx(b0_u, temp1)
