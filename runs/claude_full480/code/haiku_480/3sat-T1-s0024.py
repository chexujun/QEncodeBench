from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0, a1, a2, a3, a4 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]
    
    # Initialize result ancilla to 1 (formula is true unless a false condition is satisfied)
    qc.x(a4)
    
    # Condition 1: (x0=1, x1=1, x2=1) - makes formula false
    qc.ccx(x0, x1, a0)
    qc.ccx(a0, x2, a1)
    qc.ccx(a1, a4, a4)
    qc.ccx(a0, x2, a1)
    qc.ccx(x0, x1, a0)
    
    # Condition 2: (NOT x0, x1, x2) - makes formula false
    qc.x(a0)
    qc.cx(x0, a0)
    qc.ccx(a0, x1, a1)
    qc.ccx(a1, x2, a2)
    qc.ccx(a2, a4, a4)
    qc.ccx(a1, x2, a2)
    qc.ccx(a0, x1, a1)
    qc.cx(x0, a0)
    qc.x(a0)
    
    # Condition 3: (NOT x0, x1, NOT x2) - makes formula false
    qc.x(a0)
    qc.cx(x0, a0)
    qc.x(a2)
    qc.cx(x2, a2)
    qc.ccx(a0, x1, a1)
    qc.ccx(a1, a2, a3)
    qc.ccx(a3, a4, a4)
    qc.ccx(a1, a2, a3)
    qc.ccx(a0, x1, a1)
    qc.cx(x2, a2)
    qc.x(a2)
    qc.cx(x0, a0)
    qc.x(a0)
    
    # Condition 4: (NOT x0, NOT x1, x2) - makes formula false
    qc.x(a0)
    qc.cx(x0, a0)
    qc.x(a1)
    qc.cx(x1, a1)
    qc.ccx(a0, a1, a2)
    qc.ccx(a2, x2, a3)
    qc.ccx(a3, a4, a4)
    qc.ccx(a2, x2, a3)
    qc.ccx(a0, a1, a2)
    qc.cx(x1, a1)
    qc.x(a1)
    qc.cx(x0, a0)
    qc.x(a0)
    
    # Apply phase to result ancilla
    qc.z(a4)
    
    # Uncompute condition 4 (reverse order)
    qc.x(a0)
    qc.cx(x0, a0)
    qc.x(a1)
    qc.cx(x1, a1)
    qc.ccx(a0, a1, a2)
    qc.ccx(a2, x2, a3)
    qc.ccx(a3, a4, a4)
    qc.ccx(a2, x2, a3)
    qc.ccx(a0, a1, a2)
    qc.cx(x1, a1)
    qc.x(a1)
    qc.cx(x0, a0)
    qc.x(a0)
    
    # Uncompute condition 3
    qc.x(a0)
    qc.cx(x0, a0)
    qc.x(a2)
    qc.cx(x2, a2)
    qc.ccx(a0, x1, a1)
    qc.ccx(a1, a2, a3)
    qc.ccx(a3, a4, a4)
    qc.ccx(a1, a2, a3)
    qc.ccx(a0, x1, a1)
    qc.cx(x2, a2)
    qc.x(a2)
    qc.cx(x0, a0)
    qc.x(a0)
    
    # Uncompute condition 2
    qc.x(a0)
    qc.cx(x0, a0)
    qc.ccx(a0, x1, a1)
    qc.ccx(a1, x2, a2)
    qc.ccx(a2, a4, a4)
    qc.ccx(a1, x2, a2)
    qc.ccx(a0, x1, a1)
    qc.cx(x0, a0)
    qc.x(a0)
    
    # Uncompute condition 1
    qc.ccx(x0, x1, a0)
    qc.ccx(a0, x2, a1)
    qc.ccx(a1, a4, a4)
    qc.ccx(a0, x2, a1)
    qc.ccx(x0, x1, a0)
    
    # Uncompute initialization
    qc.x(a4)
