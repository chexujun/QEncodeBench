from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for pattern matching: pattern "0111" as contiguous substring.
    Marks states (applies -1 phase) where pattern matches at any offset 0..4.
    """
    
    # Step 1: COMPUTE — check pattern match at each offset
    for offset in range(5):  # offsets 0, 1, 2, 3, 4
        # Pattern "0111": s[offset]=0, s[offset+1]=1, s[offset+2]=1, s[offset+3]=1
        aux = ancilla_qubits[5]
        
        # Compute NOT s[offset] into aux
        qc.x(aux)
        qc.cx(problem_qubits[offset], aux)
        
        # Compute: ancilla[offset] ^= (NOT s[offset]) AND s[offset+1] AND s[offset+2] AND s[offset+3]
        qc.mcx(
            [aux, problem_qubits[offset+1], problem_qubits[offset+2], problem_qubits[offset+3]],
            ancilla_qubits[offset]
        )
        
        # Uncompute aux
        qc.cx(problem_qubits[offset], aux)
        qc.x(aux)
    
    # Step 2: COMPUTE — OR all match results into ancilla[5]
    # Compute: OR(a0, a1, a2, a3, a4) = NOT(AND(NOT a0, NOT a1, NOT a2, NOT a3, NOT a4))
    
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    qc.mcx(ancilla_qubits[0:5], ancilla_qubits[5])
    qc.x(ancilla_qubits[5])
    
    # Step 3: PHASE — apply Z to mark result
    qc.z(ancilla_qubits[5])
    
    # Step 4: UNCOMPUTE — reverse OR computation
    qc.x(ancilla_qubits[5])
    qc.mcx(ancilla_qubits[0:5], ancilla_qubits[5])
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Step 5: UNCOMPUTE — reverse offset match computations (reverse order)
    for offset in range(4, -1, -1):
        aux = ancilla_qubits[5]
        
        qc.mcx(
            [aux, problem_qubits[offset+1], problem_qubits[offset+2], problem_qubits[offset+3]],
            ancilla_qubits[offset]
        )
        
        qc.cx(problem_qubits[offset], aux)
        qc.x(aux)
