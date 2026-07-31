from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits
    temp = ancilla_qubits[0]
    anc = ancilla_qubits[1]
    
    # Compute the predicate: (NOT x[0]) AND (x[1] XOR x[2])
    # This identifies subsets of [2, 5, 5] that sum to 5
    
    # Step 1: Compute temp = x[1] XOR x[2]
    qc.cx(x1, temp)
    qc.cx(x2, temp)
    
    # Step 2: Compute anc = (NOT x[0]) AND temp
    qc.x(x0)  # flip x[0] to create NOT x[0]
    qc.ccx(x0, temp, anc)  # anc = (NOT x[0]) AND temp
    qc.x(x0)  # restore x[0]
    
    # Step 3: Apply phase flip to marked states
    qc.z(anc)
    
    # Step 4: Uncompute (reverse all steps)
    qc.x(x0)
    qc.ccx(x0, temp, anc)
    qc.x(x0)
    qc.cx(x2, temp)
    qc.cx(x1, temp)
