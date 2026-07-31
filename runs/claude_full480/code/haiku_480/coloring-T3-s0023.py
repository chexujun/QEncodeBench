from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4)]
    
    # Ancilla layout:
    # a0: same_color predicate (reused for each edge)
    # a1, a2: work qubits for OR computation
    # a3: temporary work qubit
    # a4: running OR of all violations (same_color predicates)
    
    for u, v in edges:
        # Compute same_color(u, v) into a0
        compute_same_color(qc, u, v, problem_qubits, ancilla_qubits)
        
        # Update a4 = a4 OR a0
        update_or_inplace(qc, ancilla_qubits[0], ancilla_qubits[4], ancilla_qubits[1])
        
        # Uncompute same_color from a0
        uncompute_same_color(qc, u, v, problem_qubits, ancilla_qubits)
    
    # Apply negated-control phase: phase -1 iff a4 = 0
    qc.x(ancilla_qubits[4])
    qc.z(ancilla_qubits[4])
    qc.x(ancilla_qubits[4])
    
    # Uncompute in reverse order
    for u, v in reversed(edges):
        compute_same_color(qc, u, v, problem_qubits, ancilla_qubits)
        uncompute_or_inplace(qc, ancilla_qubits[0], ancilla_qubits[4], ancilla_qubits[1])
        uncompute_same_color(qc, u, v, problem_qubits, ancilla_qubits)

def compute_same_color(qc: QuantumCircuit, u: int, v: int, 
                       problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u+1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v+1]
    
    result = ancilla_qubits[0]
    eq_b0 = ancilla_qubits[1]
    eq_b1 = ancilla_qubits[2]
    temp = ancilla_qubits[3]
    
    # Compute b0_u == b0_v into eq_b0
    qc.cx(b0_u, eq_b0)
    qc.cx(b0_v, eq_b0)
    qc.x(eq_b0)  # eq_b0 = NOT(b0_u XOR b0_v)
    
    # Compute b1_u == b1_v into eq_b1
    qc.cx(b1_u, eq_b1)
    qc.cx(b1_v, eq_b1)
    qc.x(eq_b1)  # eq_b1 = NOT(b1_u XOR b1_v)
    
    # Compute term1 = eq_b0 AND eq_b1
    qc.toffoli(eq_b0, eq_b1, temp)
    qc.cx(temp, result)  # result = term1
    
    # Compute term2 = (NOT b0_u AND NOT b1_u AND b0_v AND b1_v)
    qc.x(b0_u)
    qc.x(b1_u)
    qc.toffoli(b0_u, b1_u, temp)
    qc.toffoli(temp, b0_v, eq_b0)
    qc.toffoli(eq_b0, b1_v, temp)
    qc.cx(temp, result)  # result = result OR term2
    qc.toffoli(eq_b0, b1_v, temp)
    qc.toffoli(b0_u, b1_u, temp)
    qc.x(b0_u)
    qc.x(b1_u)
    
    # Compute term3 = (b0_u AND b1_u AND NOT b0_v AND NOT b1_v)
    qc.x(b0_v)
    qc.x(b1_v)
    qc.toffoli(b0_u, b1_u, temp)
    qc.toffoli(temp, b0_v, eq_b0)
    qc.toffoli(eq_b0, b1_v, temp)
    qc.cx(temp, result)  # result = result OR term3
    qc.toffoli(eq_b0, b1_v, temp)
    qc.toffoli(b0_u, b1_u, temp)
    qc.x(b0_v)
    qc.x(b1_v)
    
    # Uncompute eq_b0 and eq_b1
    qc.x(eq_b1)
    qc.cx(b1_v, eq_b1)
    qc.cx(b1_u, eq_b1)
    qc.x(eq_b0)
    qc.cx(b0_v, eq_b0)
    qc.cx(b0_u, eq_b0)

def uncompute_same_color(qc: QuantumCircuit, u: int, v: int, 
                         problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u+1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v+1]
    
    result = ancilla_qubits[0]
    eq_b0 = ancilla_qubits[1]
    eq_b1 = ancilla_qubits[2]
    temp = ancilla_qubits[3]
    
    # Reverse of compute_same_color
    qc.cx(b0_u, eq_b0)
    qc.cx(b0_v, eq_b0)
    qc.x(eq_b0)
    
    qc.cx(b1_u, eq_b1)
    qc.cx(b1_v, eq_b1)
    qc.x(eq_b1)
    
    qc.toffoli(eq_b0, b1_v, temp)
    qc.cx(temp, result)
    qc.toffoli(b0_u, b1_u, temp)
    qc.x(b0_v)
    qc.x(b1_v)
    qc.toffoli(eq_b0, b1_v, temp)
    qc.toffoli(temp, b0_v, eq_b0)
    qc.toffoli(b0_u, b1_u, temp)
    qc.cx(temp, result)
    qc.x(b0_u)
    qc.x(b1_u)
    qc.toffoli(eq_b0, b1_v, temp)
    qc.toffoli(temp, b0_v, eq_b0)
    qc.toffoli(b0_u, b1_u, temp)
    qc.cx(temp, result)
    qc.x(b0_u)
    qc.x(b1_u)
    
    qc.toffoli(eq_b0, eq_b1, temp)
    qc.cx(temp, result)

def update_or_inplace(qc: QuantumCircuit, pred: int, running_or: int, work: int) -> None:
    # Update running_or = running_or OR pred
    qc.x(work)
    qc.cx(running_or, work)  # work = NOT running_or
    qc.toffoli(work, pred, running_or)
    qc.cx(running_or, work)  # work = 1
    qc.x(work)  # work = 0

def uncompute_or_inplace(qc: QuantumCircuit, pred: int, running_or: int, work: int) -> None:
    # Undo update_or_inplace
    qc.x(work)
    qc.cx(running_or, work)
    qc.toffoli(work, pred, running_or)
    qc.cx(running_or, work)
    qc.x(work)
