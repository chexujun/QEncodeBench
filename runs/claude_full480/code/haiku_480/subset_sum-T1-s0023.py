from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # Mark states where sum of selected elements equals 5
    # a = [5, 3, 2], target T = 5
    # Marked states: (p0=1, p1=0, p2=0) sum=5, and (p0=0, p1=1, p2=1) sum=5
    
    # Compute into a[0]: (p0 AND NOT p1 AND NOT p2) OR (NOT p0 AND p1 AND p2)
    
    # First term: p0 AND NOT p1 AND NOT p2
    qc.x(p[1])
    qc.x(p[2])
    qc.mcx([p[0], p[1], p[2]], a[0])
    qc.x(p[2])
    qc.x(p[1])
    
    # Second term: NOT p0 AND p1 AND p2
    qc.x(p[0])
    qc.mcx([p[0], p[1], p[2]], a[0])
    qc.x(p[0])
    
    # Apply phase
    qc.z(a[0])
    
    # Uncompute second term
    qc.x(p[0])
    qc.mcx([p[0], p[1], p[2]], a[0])
    qc.x(p[0])
    
    # Uncompute first term
    qc.x(p[1])
    qc.x(p[2])
    qc.mcx([p[0], p[1], p[2]], a[0])
    qc.x(p[2])
    qc.x(p[1])
