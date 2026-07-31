from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    clauses = [
        ([0, 1, 2], [False, True, False]),
        ([1, 3, 4], [False, True, True]),
        ([0, 3, 5], [False, True, False]),
        ([0, 4, 5], [False, False, False]),
        ([1, 4, 5], [True, False, False]),
        ([0, 2, 3], [True, True, False]),
        ([0, 3, 5], [False, False, False]),
        ([0, 1, 2], [True, True, False]),
        ([0, 1, 4], [False, True, False]),
        ([0, 3, 4], [True, True, False]),
        ([1, 2, 5], [True, True, True]),
        ([0, 3, 4], [False, True, False]),
    ]
    
    clause_sat = ancilla_qubits[:12]
    temp_work = ancilla_qubits[12]
    
    for clause_idx, (var_indices, is_positive) in enumerate(clauses):
        v0, v1, v2 = var_indices
        pos0, pos1, pos2 = is_positive
        q0, q1, q2 = problem_qubits[v0], problem_qubits[v1], problem_qubits[v2]
        
        anc = clause_sat[clause_idx]
        
        # Compute (NOT lit0) AND (NOT lit1) AND (NOT lit2) into anc
        # where lit_i = +var_i if pos_i else -var_i
        # NOT lit_i = NOT var_i if pos_i else var_i
        
        # Compute NOT lit0
        if pos0:
            qc.cx(q0, temp_work)
            qc.x(temp_work)
        else:
            qc.cx(q0, temp_work)
        
        # temp_work now holds NOT lit0. AND with NOT lit1.
        if pos1:
            qc.cx(q1, anc)
            qc.x(anc)
            qc.ccx(anc, temp_work, anc)
            qc.cx(q1, anc)
            qc.x(anc)
        else:
            qc.ccx(q1, temp_work, anc)
        
        # anc now holds (NOT lit0) AND (NOT lit1). AND with NOT lit2.
        if pos2:
            qc.cx(q2, temp_work)
            qc.x(temp_work)
            qc.ccx(temp_work, anc, anc)
            qc.x(temp_work)
            qc.cx(q2, temp_work)
        else:
            qc.ccx(q2, anc, anc)
        
        # Uncompute temp_work (which should now be 0 after the sequence above)
        if pos0:
            qc.x(temp_work)
            qc.cx(q0, temp_work)
        else:
            qc.cx(q0, temp_work)
        
        # anc now holds (NOT lit0) AND (NOT lit1) AND (NOT lit2), which is 1 iff clause is NOT satisfied
        # Flip to get satisfaction
        qc.x(anc)
    
    # Now AND all clause_sat values using mcp (multi-controlled phase gate)
    # mcp with angle=pi is equivalent to applying -1 phase when all controls are 1
    qc.mcp(math.pi, clause_sat, temp_work)
    
    # Uncompute clause satisfactions
    for clause_idx in range(len(clauses)):
        qc.x(clause_sat[clause_idx])
    
    # Uncompute temp_work (clean up)
    for clause_idx, (var_indices, is_positive) in enumerate(clauses):
        v0, v1, v2 = var_indices
        pos0, pos1, pos2 = is_positive
        q0, q1, q2 = problem_qubits[v0], problem_qubits[v1], problem_qubits[v2]
        
        anc = clause_sat[clause_idx]
        
        if pos2:
            qc.cx(q2, temp_work)
            qc.x(temp_work)
            qc.ccx(temp_work, anc, anc)
            qc.x(temp_work)
            qc.cx(q2, temp_work)
        else:
            qc.ccx(q2, anc, anc)
        
        if pos1:
            qc.cx(q1, anc)
            qc.x(anc)
            qc.ccx(anc, temp_work, anc)
            qc.cx(q1, anc)
            qc.x(anc)
        else:
            qc.ccx(q1, temp_work, anc)
        
        if pos0:
            qc.cx(q0, temp_work)
            qc.x(temp_work)
        else:
            qc.cx(q0, temp_work)
