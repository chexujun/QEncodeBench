from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    # Clause definitions: each is (variable_index, is_positive)
    # is_positive=True means use qubit as-is, False means use NOT qubit
    clauses = [
        [(1, True), (3, False), (6, True)],    # x1 OR NOT x3 OR x6
        [(3, False), (5, True), (6, False)],   # NOT x3 OR x5 OR NOT x6
        [(0, True), (3, False), (4, True)],    # x0 OR NOT x3 OR x4
        [(1, True), (3, False), (5, True)],    # x1 OR NOT x3 OR x5
        [(0, False), (3, True), (7, True)],    # NOT x0 OR x3 OR x7
        [(0, True), (2, True), (3, True)],     # x0 OR x2 OR x3
        [(3, True), (4, False), (6, True)],    # x3 OR NOT x4 OR x6
        [(2, False), (5, True), (7, False)],   # NOT x2 OR x5 OR NOT x7
    ]
    
    # COMPUTE phase: compute each clause into ancilla_qubits[0..7]
    for i, clause in enumerate(clauses):
        compute_or_3bit(qc, problem_qubits, clause, ancilla_qubits[i], ancilla_qubits[8])
    
    # Compute AND of all 8 clause ancillas using a chain of Toffoli gates
    # Results stored back in ancilla_qubits with ancilla_qubits[8] as final result
    and_gates = []
    
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[8])
    and_gates.append((0, 1, 8))
    
    qc.ccx(ancilla_qubits[8], ancilla_qubits[2], ancilla_qubits[0])
    and_gates.append((8, 2, 0))
    
    qc.ccx(ancilla_qubits[0], ancilla_qubits[3], ancilla_qubits[8])
    and_gates.append((0, 3, 8))
    
    qc.ccx(ancilla_qubits[8], ancilla_qubits[4], ancilla_qubits[0])
    and_gates.append((8, 4, 0))
    
    qc.ccx(ancilla_qubits[0], ancilla_qubits[5], ancilla_qubits[8])
    and_gates.append((0, 5, 8))
    
    qc.ccx(ancilla_qubits[8], ancilla_qubits[6], ancilla_qubits[0])
    and_gates.append((8, 6, 0))
    
    qc.ccx(ancilla_qubits[0], ancilla_qubits[7], ancilla_qubits[8])
    and_gates.append((0, 7, 8))
    
    # Apply Z phase to mark solutions (phase -1 when all clauses are satisfied)
    qc.z(ancilla_qubits[8])
    
    # Uncompute AND tree in reverse (gates are self-inverse)
    for c1_idx, c2_idx, target_idx in reversed(and_gates):
        qc.ccx(ancilla_qubits[c1_idx], ancilla_qubits[c2_idx], ancilla_qubits[target_idx])
    
    # UNCOMPUTE phase: uncompute each clause in reverse order
    for i, clause in enumerate(reversed(clauses)):
        clause_idx = 7 - i
        uncompute_or_3bit(qc, problem_qubits, clause, ancilla_qubits[clause_idx], ancilla_qubits[8])


def compute_or_3bit(qc: QuantumCircuit, problem_qubits: list[int], 
                   clause: list, result_qubit: int, aux_qubit: int) -> None:
    """Compute (lit0 OR lit1 OR lit2) into result_qubit, returning aux_qubit to |0>."""
    q0_idx, q0_pos = clause[0]
    q1_idx, q1_pos = clause[1]
    q2_idx, q2_pos = clause[2]
    
    q0 = problem_qubits[q0_idx]
    q1 = problem_qubits[q1_idx]
    q2 = problem_qubits[q2_idx]
    
    # To compute OR, we compute NOT(AND of complements) = NOT(NOT lit0 AND NOT lit1 AND NOT lit2)
    # Flip qubits to get negated literals
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)
    if q2_pos:
        qc.x(q2)
    
    # Compute AND(flipped q0, flipped q1) into aux_qubit
    qc.ccx(q0, q1, aux_qubit)
    
    # Restore q0, q1
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)
    
    # Compute AND(aux_qubit, flipped q2) into result_qubit
    qc.ccx(aux_qubit, q2, result_qubit)
    
    # Restore q2
    if q2_pos:
        qc.x(q2)
    
    # Negate to get OR
    qc.x(result_qubit)
    
    # Uncompute aux_qubit
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)
    
    qc.ccx(q0, q1, aux_qubit)
    
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)


def uncompute_or_3bit(qc: QuantumCircuit, problem_qubits: list[int], 
                     clause: list, result_qubit: int, aux_qubit: int) -> None:
    """Reverse compute_or_3bit: return result_qubit to |0>."""
    q0_idx, q0_pos = clause[0]
    q1_idx, q1_pos = clause[1]
    q2_idx, q2_pos = clause[2]
    
    q0 = problem_qubits[q0_idx]
    q1 = problem_qubits[q1_idx]
    q2 = problem_qubits[q2_idx]
    
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)
    
    qc.ccx(q0, q1, aux_qubit)
    
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)
    
    qc.x(result_qubit)
    
    if q2_pos:
        qc.x(q2)
    
    qc.ccx(aux_qubit, q2, result_qubit)
    
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)
    
    qc.ccx(q0, q1, aux_qubit)
    
    if q0_pos:
        qc.x(q0)
    if q1_pos:
        qc.x(q1)
    if q2_pos:
        qc.x(q2)
