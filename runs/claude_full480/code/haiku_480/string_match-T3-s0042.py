from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Pattern "0?00" matches at offsets 0-4
    # Offset i: check if s_i == 0 AND s_{i+2} == 0 AND s_{i+3} == 0
    offsets = [
        [0, 2, 3],  # offset 0
        [1, 3, 4],  # offset 1
        [2, 4, 5],  # offset 2
        [3, 5, 6],  # offset 3
        [4, 6, 7],  # offset 4
    ]
    
    # Compute each offset match into ancilla_qubits[0-4]
    # For offset i: compute (s[j] == 0 for all j in offsets[i]) into ancilla[i]
    for idx, offset_qubits in enumerate(offsets):
        # To test if s[j] == 0, flip qubits with X, apply mcx, flip back
        for q in offset_qubits:
            qc.x(problem_qubits[q])
        qc.mcx([problem_qubits[q] for q in offset_qubits], ancilla_qubits[idx])
        for q in offset_qubits:
            qc.x(problem_qubits[q])
    
    # Compute OR of all 5 match flags into ancilla_qubits[5]
    # Iteratively: result = a[0] OR a[1] OR a[2] OR a[3] OR a[4]
    result = ancilla_qubits[5]
    for i in range(5):
        a = ancilla_qubits[i]
        # result := result OR a, using: temp=1; CX(result,temp); CX(a,temp); CCX(result,a,temp); X(temp); then propagate
        # Simpler: use controlled operations to set result=1 if any input is 1
        # First CX to XOR, then correct for the (1,1) case using CCX
        qc.cx(a, result)
        qc.ccx(a, result, ancilla_qubits[(i + 5) % 6])  # use another ancilla temporarily
        qc.cx(ancilla_qubits[(i + 5) % 6], result)
        qc.ccx(a, result, ancilla_qubits[(i + 5) % 6])  # uncompute temp
    
    # Apply phase flip to result qubit
    qc.z(result)
    
    # Uncompute the OR
    for i in range(4, -1, -1):
        a = ancilla_qubits[i]
        qc.ccx(a, result, ancilla_qubits[(i + 5) % 6])  # uncompute temp
        qc.cx(ancilla_qubits[(i + 5) % 6], result)
        qc.ccx(a, result, ancilla_qubits[(i + 5) % 6])  # re-compute temp for uncompute
        qc.cx(a, result)
    
    # Uncompute each offset match
    for idx, offset_qubits in enumerate(offsets):
        for q in offset_qubits:
            qc.x(problem_qubits[q])
        qc.mcx([problem_qubits[q] for q in offset_qubits], ancilla_qubits[idx])
        for q in offset_qubits:
            qc.x(problem_qubits[q])
