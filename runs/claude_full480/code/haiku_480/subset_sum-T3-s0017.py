from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Subset sum oracle: mark states where selected elements sum to 10
    # a = [15, 5, 10, 4, 2], target = 10
    # Only the state |0,0,1,0,0> (selecting only a[2]=10) satisfies the constraint
    
    # We check: p[0]=0 AND p[1]=0 AND p[2]=1 AND p[3]=0 AND p[4]=0
    
    # Use ancillas to compute intermediate values
    not_p0 = ancilla_qubits[0]
    not_p1 = ancilla_qubits[1]
    not_p3 = ancilla_qubits[2]
    not_p4 = ancilla_qubits[3]
    flag = ancilla_qubits[4]
    
    # Compute NOT values for qubits that should be 0
    qc.cx(problem_qubits[0], not_p0)
    qc.x(not_p0)
    
    qc.cx(problem_qubits[1], not_p1)
    qc.x(not_p1)
    
    qc.cx(problem_qubits[3], not_p3)
    qc.x(not_p3)
    
    qc.cx(problem_qubits[4], not_p4)
    qc.x(not_p4)
    
    # Compute AND: flag = not_p0 AND not_p1 AND p[2] AND not_p3 AND not_p4
    qc.mcx([not_p0, not_p1, problem_qubits[2], not_p3, not_p4], flag)
    
    # Apply phase flip
    qc.z(flag)
    
    # Uncompute the AND
    qc.mcx([not_p0, not_p1, problem_qubits[2], not_p3, not_p4], flag)
    
    # Uncompute the NOT values
    qc.x(not_p4)
    qc.cx(problem_qubits[4], not_p4)
    
    qc.x(not_p3)
    qc.cx(problem_qubits[3], not_p3)
    
    qc.x(not_p1)
    qc.cx(problem_qubits[1], not_p1)
    
    qc.x(not_p0)
    qc.cx(problem_qubits[0], not_p0)
