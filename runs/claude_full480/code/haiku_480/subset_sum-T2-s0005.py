from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Problem: sum of selected elements from [10, 2, 8, 9] equals 2
    # Only solution: x = (0, 1, 0, 0) – select only a[1] = 2
    # Condition: (NOT x0) AND x1 AND (NOT x2) AND (NOT x3)
    
    a = ancilla_qubits[0]
    
    # Compute: flip qubits to match condition pattern
    qc.x(problem_qubits[0])  # NOT x0
    qc.x(problem_qubits[2])  # NOT x2
    qc.x(problem_qubits[3])  # NOT x3
    
    # 4-controlled X: flip ancilla when all problem qubits are 1
    qc.mcx(problem_qubits, a, ancilla_qubits=ancilla_qubits[1:], mode='v-chain')
    
    # Phase: apply -1 when ancilla is 1
    qc.z(a)
    
    # Uncompute: reverse the multi-controlled X
    qc.mcx(problem_qubits, a, ancilla_qubits=ancilla_qubits[1:], mode='v-chain')
    
    # Uncompute: undo the X flips
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[0])
