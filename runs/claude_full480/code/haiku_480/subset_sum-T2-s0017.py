from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    anc = ancilla_qubits
    
    # Subset sum problem: a = [4, 9, 1, 9], target T = 9
    # Solutions are subsets {1} and {3}, corresponding to states x=0010 and x=1000
    # i.e., (p[0]=0, p[1]=1, p[2]=0, p[3]=0) or (p[0]=0, p[1]=0, p[2]=0, p[3]=1)
    # Simplified condition: NOT p[0] AND NOT p[2] AND (p[1] OR p[3])
    
    # Allocate ancillas
    condition_flag = anc[0]
    p1_or_p3 = anc[1]
    temp_and = anc[2]
    
    # Compute p[1] AND p[3]
    qc.mcx([p[1], p[3]], temp_and)
    
    # Compute p[1] OR p[3] using: a OR b = a XOR b XOR (a AND b)
    qc.cx(p[1], p1_or_p3)
    qc.cx(p[3], p1_or_p3)
    qc.cx(temp_and, p1_or_p3)
    
    # Compute NOT p[0] AND NOT p[2] AND (p[1] OR p[3])
    qc.x(p[0])
    qc.x(p[2])
    qc.mcx([p[0], p[2], p1_or_p3], condition_flag)
    qc.x(p[0])
    qc.x(p[2])
    
    # Apply phase: -1 if condition is true
    qc.z(condition_flag)
    
    # Uncompute (reverse order)
    qc.x(p[0])
    qc.x(p[2])
    qc.mcx([p[0], p[2], p1_or_p3], condition_flag)
    qc.x(p[0])
    qc.x(p[2])
    
    qc.cx(temp_and, p1_or_p3)
    qc.cx(p[3], p1_or_p3)
    qc.cx(p[1], p1_or_p3)
    
    qc.mcx([p[1], p[3]], temp_and)
