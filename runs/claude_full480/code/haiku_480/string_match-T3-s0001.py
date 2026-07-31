from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    offsets = [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), (5, 6, 7)]
    
    # Allocate: ancilla[0:6] for flags, ancilla[6] for result
    flags = ancilla_qubits[0:6]
    result = ancilla_qubits[6]
    
    # Compute: flag[i] = 1 iff pattern matches at offset i
    for i, (o1, o2, o3) in enumerate(offsets):
        qc.mcx([problem_qubits[o1], problem_qubits[o2], problem_qubits[o3]], flags[i])
    
    # Compute: OR all flags into result
    # result = flags[0]
    qc.cx(flags[0], result)
    
    # result = result OR flags[i] for i = 1..5
    # Use flags[i-1] as temp qubit (reuse after each step)
    for i in range(1, 6):
        temp = flags[i - 1]
        qc.ccx(flags[i], result, temp)
        qc.cx(flags[i], result)
        qc.cx(temp, result)
    
    # Phase: mark the state with -1 phase
    qc.z(result)
    
    # Uncompute: reverse OR operations
    for i in range(5, 0, -1):
        temp = flags[i - 1]
        qc.cx(temp, result)
        qc.cx(flags[i], result)
        qc.ccx(flags[i], result, temp)
    
    # Uncompute: undo first OR
    qc.cx(flags[0], result)
    
    # Uncompute: undo flag computations
    for i, (o1, o2, o3) in enumerate(offsets):
        qc.mcx([problem_qubits[o1], problem_qubits[o2], problem_qubits[o3]], flags[i])
