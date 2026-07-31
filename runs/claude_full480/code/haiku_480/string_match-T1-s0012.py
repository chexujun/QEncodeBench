from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern: "0?01?" means s[0]=0, s[2]=0, s[3]=1
    # Compute: f(x) = (NOT s[0]) AND (NOT s[2]) AND s[3]
    
    # Flip s[0] and s[2] to represent their negations
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[2])
    
    # Compute: ancilla[0] = (NOT s[0]) AND (NOT s[2])
    qc.ccx(problem_qubits[0], problem_qubits[2], ancilla_qubits[0])
    
    # Compute: ancilla[1] = ancilla[0] AND s[3]
    qc.ccx(ancilla_qubits[0], problem_qubits[3], ancilla_qubits[1])
    
    # Apply phase flip
    qc.z(ancilla_qubits[1])
    
    # Uncompute: reverse to restore ancillas to |0>
    qc.ccx(ancilla_qubits[0], problem_qubits[3], ancilla_qubits[1])
    qc.ccx(problem_qubits[0], problem_qubits[2], ancilla_qubits[0])
    
    # Flip s[0] and s[2] back to original values
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[0])
