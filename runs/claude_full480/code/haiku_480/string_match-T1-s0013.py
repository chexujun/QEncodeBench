from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Pattern: 011101 (positions 0-5)
    # Need: x[0]=0, x[1]=1, x[2]=1, x[3]=1, x[4]=0, x[5]=1
    
    # Flip qubits that need to be 0 in the pattern (positions 0 and 4)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[4])
    
    # Prepare ancilla to |1> to receive the phase
    qc.x(ancilla_qubits[0])
    
    # Apply multi-controlled phase gate (π)
    # This applies phase e^(iπ) = -1 when all problem qubits are 1
    qc.mcp(pi, problem_qubits, ancilla_qubits[0])
    
    # Restore ancilla to |0>
    qc.x(ancilla_qubits[0])
    
    # Flip back qubits that were flipped initially
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[4])
