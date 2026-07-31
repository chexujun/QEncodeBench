from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a0, a1, a2, result = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    
    # Compute a0 = x0 AND x1 AND NOT x2 AND NOT x3 (detects solution {0,1})
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x0, x1, x2, x3], a0)
    qc.x(x3)
    qc.x(x2)
    
    # Compute a1 = x0 AND NOT x1 AND NOT x2 AND x3 (detects solution {0,3})
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2, x3], a1)
    qc.x(x2)
    qc.x(x1)
    
    # Compute a2 = NOT x0 AND NOT x1 AND x2 AND x3 (detects solution {2,3})
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2, x3], a2)
    qc.x(x1)
    qc.x(x0)
    
    # Compute result = a0 XOR a1 XOR a2 (equals OR since conditions are mutually exclusive)
    qc.cx(a0, result)
    qc.cx(a1, result)
    qc.cx(a2, result)
    
    # Apply phase -1
    qc.z(result)
    
    # Uncompute result
    qc.cx(a2, result)
    qc.cx(a1, result)
    qc.cx(a0, result)
    
    # Uncompute a2
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2, x3], a2)
    qc.x(x1)
    qc.x(x0)
    
    # Uncompute a1
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2, x3], a1)
    qc.x(x2)
    qc.x(x1)
    
    # Uncompute a0
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x0, x1, x2, x3], a0)
    qc.x(x3)
    qc.x(x2)
