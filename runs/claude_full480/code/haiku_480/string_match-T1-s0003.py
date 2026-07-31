from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p0, p1, p2, p3, p4, p5 = problem_qubits
    a0, a1 = ancilla_qubits
    
    # Pattern: "0??010"
    # Apply phase -1 if x[0]=0, x[3]=0, x[4]=1, x[5]=0
    
    # Compute: a0 = (NOT p0) AND (NOT p3)
    qc.x(p0)
    qc.x(p3)
    qc.ccx(p0, p3, a0)
    qc.x(p3)
    qc.x(p0)
    
    # Compute: a1 = p4 AND (NOT p5)
    qc.x(p5)
    qc.ccx(p4, p5, a1)
    qc.x(p5)
    
    # Phase: apply controlled-Z if both a0 and a1 are 1
    qc.cz(a0, a1)
    
    # Uncompute: a1 = p4 AND (NOT p5)
    qc.x(p5)
    qc.ccx(p4, p5, a1)
    qc.x(p5)
    
    # Uncompute: a0 = (NOT p0) AND (NOT p3)
    qc.x(p0)
    qc.x(p3)
    qc.ccx(p0, p3, a0)
    qc.x(p3)
    qc.x(p0)
