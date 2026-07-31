from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Mark states where sum = 8*x0 + 4*x1 + 9*x2 + 3*x3 = 20
    # Only state |1101> satisfies this (8+9+3=20)
    
    # COMPUTE PHASE:
    # Flip x1 to make all conditions positive (x0=1, x1=1 after flip, x2=1, x3=1)
    qc.x(problem_qubits[1])
    
    # Compute AND of all 4 problem qubits using Toffoli gates
    # Temp storage for intermediate AND results
    qc.ccx(problem_qubits[0], problem_qubits[1], ancilla_qubits[0])
    qc.ccx(ancilla_qubits[0], problem_qubits[2], ancilla_qubits[1])
    qc.ccx(ancilla_qubits[1], problem_qubits[3], ancilla_qubits[4])
    
    # Apply Z phase to mark the solution state
    qc.z(ancilla_qubits[4])
    
    # UNCOMPUTE PHASE:
    # Reverse the Toffoli gates to restore ancillas to |0>
    qc.ccx(ancilla_qubits[1], problem_qubits[3], ancilla_qubits[4])
    qc.ccx(ancilla_qubits[0], problem_qubits[2], ancilla_qubits[1])
    qc.ccx(problem_qubits[0], problem_qubits[1], ancilla_qubits[0])
    
    # Flip x1 back to original value
    qc.x(problem_qubits[1])
