from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0, a1, a2, a3, final = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]
    
    # Compute: For each clause, mark when it's false
    
    # Clause 1: NOT x0 OR NOT x1 OR NOT x2
    # False when: x0=1 AND x1=1 AND x2=1
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    # Clause 2: x0 OR NOT x1 OR NOT x2
    # False when: x0=0 AND x1=1 AND x2=1
    qc.x(x0)
    qc.mcx([x0, x1, x2], a1)
    qc.x(x0)
    
    # Clause 3: NOT x0 OR x1 OR NOT x2
    # False when: x0=1 AND x1=0 AND x2=1
    qc.x(x1)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x1)
    
    # Clause 4: NOT x0 OR NOT x1 OR x2
    # False when: x0=1 AND x1=1 AND x2=0
    qc.x(x2)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x2)
    
    # Convert false flags to true flags
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    
    # AND them together
    qc.mcx([a0, a1, a2, a3], final)
    
    # Apply phase
    qc.z(final)
    
    # Uncompute
    qc.mcx([a0, a1, a2, a3], final)
    
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    qc.x(x2)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x2)
    
    qc.x(x1)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x1)
    
    qc.x(x0)
    qc.mcx([x0, x1, x2], a1)
    qc.x(x0)
    
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
