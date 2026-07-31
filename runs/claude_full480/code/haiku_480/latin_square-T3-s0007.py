from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = ancilla_qubits
    
    # Extract low and high bits for each free cell
    b0 = [problem_qubits[2*i] for i in range(4)]
    b1 = [problem_qubits[2*i+1] for i in range(4)]
    
    # Compute predicates for Latin square constraints
    # a[0]: v[0] = 0  (free cell 0 at (0,1))
    qc.cx(b0[0], a[0])
    qc.cx(b1[0], a[0])
    qc.x(a[0])
    
    # a[1]: v[2] = 0  (free cell 2 at (1,2))
    qc.cx(b0[2], a[1])
    qc.cx(b1[2], a[1])
    qc.x(a[1])
    
    # a[2]: v[3] = 0  (free cell 3 at (2,0))
    qc.cx(b0[3], a[2])
    qc.cx(b1[3], a[2])
    qc.x(a[2])
    
    # a[3]: v[1] = 1  (free cell 1 at (1,1))
    qc.x(b1[1])
    qc.ccx(b0[1], b1[1], a[3])
    qc.x(b1[1])
    
    # Apply conditional phase using multi-controlled phase gate
    qc.x(a[5])
    qc.mcp(pi, [a[0], a[1], a[2], a[3]], a[5])
    qc.x(a[5])
    
    # Uncompute predicates in reverse order
    # Uncompute a[3]
    qc.x(b1[1])
    qc.ccx(b0[1], b1[1], a[3])
    qc.x(b1[1])
    
    # Uncompute a[2]
    qc.x(a[2])
    qc.cx(b1[3], a[2])
    qc.cx(b0[3], a[2])
    
    # Uncompute a[1]
    qc.x(a[1])
    qc.cx(b1[2], a[1])
    qc.cx(b0[2], a[1])
    
    # Uncompute a[0]
    qc.x(a[0])
    qc.cx(b1[0], a[0])
    qc.cx(b0[0], a[0])
