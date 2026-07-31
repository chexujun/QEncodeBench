from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Phase oracle for 3-SAT: (x0∨x1∨x2) ∧ (¬x0∨x1∨¬x2) ∧ (¬x0∨¬x1∨¬x2) ∧ (x0∨x1∨¬x2) ∧ (x0∨¬x1∨x2)
    
    Satisfying assignments: 011 (x0=0,x1=1,x2=1) and 100 (x0=1,x1=0,x2=0)
    Strategy: Mark each satisfying state by applying X-gates to flip to |111>, 
    then apply multi-controlled phase gate, then undo X-gates.
    """
    satisfying = [0b011, 0b100]
    
    for state in satisfying:
        # Apply X to qubits where state bit is 0 (flips to |111> after all X gates)
        for i in range(3):
            if (state >> i) & 1 == 0:
                qc.x(problem_qubits[i])
        
        # Apply multi-controlled phase gate: phase π to |111> equals phase -1
        qc.mcp(np.pi, problem_qubits[:2], problem_qubits[2])
        
        # Undo X gates to restore original state (with phase -1)
        for i in range(3):
            if (state >> i) & 1 == 0:
                qc.x(problem_qubits[i])
