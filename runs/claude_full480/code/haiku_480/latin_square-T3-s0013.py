from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Valid free cell values are: v0=0, v1=1, v2=0, v3=0
    # Encoding: value = low_bit + 2*high_bit
    # This corresponds to the constraints:
    #   q[0] = q[1]          (free cell 0 must decode to 0)
    #   q[2]=1, q[3]=0       (free cell 1 must decode to 1)
    #   q[4] = q[5]          (free cell 2 must decode to 0)
    #   q[6] = q[7]          (free cell 3 must decode to 0)
    
    # Compute XOR for equality checks
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])  # a[0] = q[0] XOR q[1]
    
    qc.cx(q[4], a[1])
    qc.cx(q[5], a[1])  # a[1] = q[4] XOR q[5]
    
    qc.cx(q[6], a[2])
    qc.cx(q[7], a[2])  # a[2] = q[6] XOR q[7]
    
    # Convert to XNOR: a[i] = 1 iff the pair is equal
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    
    # Convert q[3] so that it equals 1 in valid states
    qc.x(q[3])
    
    # Build AND tree to compute conjunction of all constraints
    qc.ccx(a[0], a[1], a[3])  # a[3] = a[0] AND a[1]
    qc.ccx(a[2], q[2], a[4])  # a[4] = a[2] AND q[2]
    qc.ccx(a[3], a[4], a[5])  # a[5] = a[3] AND a[4]
    
    # Apply phase -1 if final AND with q[3] equals 1
    qc.cz(a[5], q[3])
    
    # Uncompute AND tree (reverse order)
    qc.ccx(a[3], a[4], a[5])
    qc.ccx(a[2], q[2], a[4])
    qc.ccx(a[0], a[1], a[3])
    
    # Unflip q[3]
    qc.x(q[3])
    
    # Unflip ancillas to restore XNOR computations
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    
    # Uncompute XORs (CX is self-inverse)
    qc.cx(q[6], a[2])
    qc.cx(q[7], a[2])
    
    qc.cx(q[4], a[1])
    qc.cx(q[5], a[1])
    
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])
