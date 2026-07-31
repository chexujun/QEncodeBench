from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = ancilla_qubits[0]
    x = problem_qubits
    
    # Pattern: "10??00" means:
    # x[0] = 1, x[1] = 0, x[4] = 0, x[5] = 0 (x[2], x[3] are free)
    
    # Flip qubits that must be 0, so all required conditions use positive controls
    qc.x(x[1])
    qc.x(x[4])
    qc.x(x[5])
    
    # Compute: ancilla = x[0] AND x[1] AND x[4] AND x[5]
    # (in the flipped basis, this equals the pattern match condition)
    qc.mcx([x[0], x[1], x[4], x[5]], a)
    
    # Apply phase: -1 iff ancilla is 1 (pattern matches)
    qc.z(a)
    
    # Uncompute: return ancilla to |0>
    qc.mcx([x[0], x[1], x[4], x[5]], a)
    
    # Undo the flips
    qc.x(x[5])
    qc.x(x[4])
    qc.x(x[1])
