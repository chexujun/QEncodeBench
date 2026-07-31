from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for subset sum: apply phase -1 to states where selected 
    elements sum to target T=18. Elements: a = [8, 8, 10, 3]
    """
    a = [8, 8, 10, 3]
    target = 18
    
    # Identify all states (4-bit strings) satisfying the subset sum condition
    solutions = []
    for state in range(16):  # 2^4 possible states
        subset_sum = sum(a[i] for i in range(4) if (state >> i) & 1)
        if subset_sum == target:
            solutions.append(state)
    
    # Use first ancilla for multi-controlled phase
    ancilla = ancilla_qubits[0]
    
    # For each solution state, apply phase -1
    for state in solutions:
        # Prepare: flip problem_qubits to enforce |1> state where needed
        for i in range(4):
            if not ((state >> i) & 1):
                qc.x(problem_qubits[i])
        
        # Phase: multi-controlled Z via ancilla
        # Flip ancilla when all problem_qubits are |1>
        qc.mcx(problem_qubits, ancilla)
        # Apply Z for phase -1
        qc.z(ancilla)
        # Uncompute ancilla
        qc.mcx(problem_qubits, ancilla)
        
        # Restore: flip problem_qubits back
        for i in range(4):
            if not ((state >> i) & 1):
                qc.x(problem_qubits[i])
