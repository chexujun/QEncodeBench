from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Condition 0: (q[0]=1) AND (q[1]=0) AND (q[2]=1) into a[0]
    qc.x(a[3])              # Compute NOT(q[1])
    qc.cx(q[1], a[3])
    qc.ccx(q[0], a[3], a[0])
    qc.ccx(q[2], a[0], a[0])
    
    # Condition 1: (q[1]=1) AND (q[2]=0) AND (q[3]=1) into a[1]
    qc.cx(q[2], a[3])       # a[3] = 1 XOR NOT(q[1]) XOR q[2]
    qc.x(a[3])              # Reset and compute NOT(q[2])
    qc.cx(q[2], a[3])
    qc.ccx(q[1], a[3], a[1])
    qc.ccx(q[3], a[1], a[1])
    
    # Condition 2: (q[2]=1) AND (q[3]=0) AND (q[4]=1) into a[2]
    qc.cx(q[3], a[3])       # a[3] = 1 XOR NOT(q[2]) XOR q[3]
    qc.x(a[3])              # Reset and compute NOT(q[3])
    qc.cx(q[3], a[3])
    qc.ccx(q[2], a[3], a[2])
    qc.ccx(q[4], a[2], a[2])
    
    # OR(a[0], a[1]) into a[0]
    qc.ccx(a[0], a[1], a[3])
    qc.cx(a[0], a[0])       # No-op but structure clarity
    qc.cx(a[1], a[0])
    qc.cx(a[3], a[0])
    
    # OR(a[0], a[2]) into a[0]
    qc.ccx(a[0], a[2], a[3])
    qc.cx(a[0], a[0])       # No-op
    qc.cx(a[2], a[0])
    qc.cx(a[3], a[0])
    
    # Apply phase
    qc.z(a[0])
    
    # Uncompute OR(a[0], a[2]) in reverse
    qc.cx(a[3], a[0])
    qc.cx(a[2], a[0])
    qc.ccx(a[0], a[2], a[3])
    
    # Uncompute OR(a[0], a[1]) in reverse
    qc.cx(a[3], a[0])
    qc.cx(a[1], a[0])
    qc.ccx(a[0], a[1], a[3])
    
    # Uncompute Condition 2
    qc.ccx(q[4], a[2], a[2])
    qc.ccx(q[2], a[3], a[2])
    qc.cx(q[3], a[3])
    qc.x(a[3])
    
    # Uncompute Condition 1
    qc.ccx(q[3], a[1], a[1])
    qc.ccx(q[1], a[3], a[1])
    qc.cx(q[2], a[3])
    qc.x(a[3])
    
    # Uncompute Condition 0
    qc.ccx(q[2], a[0], a[0])
    qc.ccx(q[0], a[3], a[0])
    qc.cx(q[1], a[3])
    qc.x(a[3])
