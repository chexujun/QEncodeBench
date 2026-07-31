from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    a0 = ancilla_qubits[0]
    
    # COMPUTE: a0 = x0 XOR x1 XOR (NOT x2) XOR x4
    # This equals 0 iff pattern "001?0" matches (x0=0, x1=0, x2=1, x4=0)
    qc.cx(x0, a0)
    qc.cx(x1, a0)
    qc.x(x2)
    qc.cx(x2, a0)
    qc.x(x2)
    qc.cx(x4, a0)
    
    # PHASE: Apply phase -1 when a0 = 0
    # Flip a0 so a0=1 iff pattern matches, apply Z, then flip back
    qc.x(a0)
    qc.z(a0)
    qc.x(a0)
    
    # UNCOMPUTE: Reverse all compute steps to return ancilla to |0>
    qc.cx(x4, a0)
    qc.x(x2)
    qc.cx(x2, a0)
    qc.x(x2)
    qc.cx(x1, a0)
    qc.cx(x0, a0)
