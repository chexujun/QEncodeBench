import numpy as np
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # Pattern "1000" at each possible offset in the 8-qubit text
    offset_indices = [
        [0, 1, 2, 3],
        [1, 2, 3, 4],
        [2, 3, 4, 5],
        [3, 4, 5, 6],
        [4, 5, 6, 7]
    ]
    
    # Initialize result ancilla to |1> for use as CZ target
    qc.x(ancilla_qubits[5])
    
    for offset in offset_indices:
        q = [problem_qubits[i] for i in offset]
        
        # Compute: match = q[0] AND NOT(q[1]) AND NOT(q[2]) AND NOT(q[3])
        # Store NOT(q[1]), NOT(q[2]), NOT(q[3]) in ancillas 0, 1, 2
        for j in range(1, 4):
            qc.cx(q[j], ancilla_qubits[j - 1])
            qc.x(ancilla_qubits[j - 1])
        
        # Compute match using MCX (multi-controlled X)
        qc.mcx([q[0], ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]], ancilla_qubits[4])
        
        # Apply phase -1 if match is true
        qc.cz(ancilla_qubits[4], ancilla_qubits[5])
        
        # Uncompute match
        qc.mcx([q[0], ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]], ancilla_qubits[4])
        
        # Uncompute NOT conditions
        for j in range(1, 4):
            qc.x(ancilla_qubits[j - 1])
            qc.cx(q[j], ancilla_qubits[j - 1])
    
    # Reset result ancilla to |0>
    qc.x(ancilla_qubits[5])
