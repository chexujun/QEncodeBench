from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for the subset sum problem: mark states where
    selected elements from [6, 10, 8, 3] sum to exactly 14.
    The only solution is selecting indices 0 and 2: 6 + 8 = 14.
    This corresponds to the state |q0=1, q1=0, q2=1, q3=0⟩.
    """
    
    # Use ancilla qubits to detect the condition
    temp_not_q1 = ancilla_qubits[0]
    temp_not_q3 = ancilla_qubits[1]
    
    # Compute NOT problem_qubits[1] into temp_not_q1
    qc.cx(problem_qubits[1], temp_not_q1)
    qc.x(temp_not_q1)
    
    # Compute NOT problem_qubits[3] into temp_not_q3
    qc.cx(problem_qubits[3], temp_not_q3)
    qc.x(temp_not_q3)
    
    # Build multi-controlled phase gate for the condition:
    # (problem_qubits[0] AND NOT problem_qubits[1] AND 
    #  problem_qubits[2] AND NOT problem_qubits[3])
    controls = [problem_qubits[0], temp_not_q1, 
                problem_qubits[2], temp_not_q3]
    
    # Apply multi-controlled phase: -1 when all controls are 1
    # mcp with 4 controls and theta=pi gives phase (-1)^(#solutions)
    qc.mcp(np.pi, controls, ancilla_qubits[4])
    
    # Uncompute the temporary qubits (reverse order)
    qc.x(temp_not_q3)
    qc.cx(problem_qubits[3], temp_not_q3)
    
    qc.x(temp_not_q1)
    qc.cx(problem_qubits[1], temp_not_q1)
