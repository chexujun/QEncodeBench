from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # [x0, x1, x2]
    a = ancilla_qubits  # [a0, a1, a2, a3]
    
    # === COMPUTE ===
    # Compute sum = 6*x[0] + 4*x[1] + 3*x[2] into a[0:4] in binary
    
    # Bit 0: a[0] = x[2]
    qc.cx(x[2], a[0])
    
    # Bit 1: a[1] = x[2] XOR x[0]
    qc.cx(x[2], a[1])
    qc.cx(x[0], a[1])
    
    # Carry from bit 1: a[3] = x[2] AND x[0]
    qc.toffoli(x[2], x[0], a[3])
    
    # Bit 2: a[2] = x[1] XOR x[0] XOR (x[2] AND x[0])
    qc.cx(x[1], a[2])
    qc.cx(x[0], a[2])
    qc.cx(a[3], a[2])
    
    # === PHASE ===
    # Apply phase -1 when sum == 3 == 0b0011
    # (a[0]=1, a[1]=1, a[2]=0, a[3]=0)
    
    # Flip a[2] and a[3] to convert condition to all-ones
    qc.x(a[2])
    qc.x(a[3])
    
    # Multi-controlled phase: applies e^(i*pi) = -1 when all controls and target are |1>
    qc.mcp(pi, [a[0], a[1], a[2], a[3]], a[0])
    
    # Flip back
    qc.x(a[3])
    qc.x(a[2])
    
    # === UNCOMPUTE ===
    # Reverse all compute steps
    qc.cx(a[3], a[2])
    qc.cx(x[0], a[2])
    qc.cx(x[1], a[2])
    qc.toffoli(x[2], x[0], a[3])
    qc.cx(x[0], a[1])
    qc.cx(x[2], a[1])
    qc.cx(x[2], a[0])
