from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 5), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4), (4, 5)]
    
    # Allocate ancillas:
    # acc0, acc1: rotating accumulators for AND
    # xor0, xor1: temporaries for XOR computation
    # constraint: temporary for constraint computation
    acc0 = ancilla_qubits[0]
    acc1 = ancilla_qubits[1]
    xor0 = ancilla_qubits[2]
    xor1 = ancilla_qubits[3]
    constraint = ancilla_qubits[4]
    
    # Forward: compute AND of all edge constraints into acc0
    qc.x(acc0)  # Initialize acc0 = 1 (all constraints satisfied)
    
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute xor0 = u0 XOR v0
        qc.cx(u0, xor0)
        qc.cx(v0, xor0)
        
        # Compute xor1 = u1 XOR v1
        qc.cx(u1, xor1)
        qc.cx(v1, xor1)
        
        # Compute constraint = xor0 OR xor1
        # Using: result = cx(a, result), cx(b, result), ccx(a, b, result)
        qc.cx(xor0, constraint)
        qc.cx(xor1, constraint)
        qc.ccx(xor0, xor1, constraint)
        
        # AND with accumulator: acc1 = acc0 AND constraint
        qc.ccx(constraint, acc0, acc1)
        
        # Swap acc0 and acc1 using CX ladder
        qc.cx(acc1, acc0)
        qc.cx(acc0, acc1)
        qc.cx(acc1, acc0)
        
        # Uncompute xors (leave constraint for later use)
        qc.cx(v0, xor0)
        qc.cx(u0, xor0)
        qc.cx(v1, xor1)
        qc.cx(u1, xor1)
    
    # Apply Z gate to encode phase for f(x)=1 states
    qc.z(acc0)
    
    # Backward: uncompute everything in reverse order
    for u, v in reversed(edges):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Swap back
        qc.cx(acc1, acc0)
        qc.cx(acc0, acc1)
        qc.cx(acc1, acc0)
        
        # Recompute xors (needed for uncomputing constraint)
        qc.cx(u0, xor0)
        qc.cx(v0, xor0)
        qc.cx(u1, xor1)
        qc.cx(v1, xor1)
        
        # Recompute constraint
        qc.cx(xor0, constraint)
        qc.cx(xor1, constraint)
        qc.ccx(xor0, xor1, constraint)
        
        # Undo AND
        qc.ccx(constraint, acc0, acc1)
        
        # Uncompute constraint
        qc.ccx(xor0, xor1, constraint)
        qc.cx(xor1, constraint)
        qc.cx(xor0, constraint)
        
        # Uncompute xors
        qc.cx(v1, xor1)
        qc.cx(u1, xor1)
        qc.cx(v0, xor0)
        qc.cx(u0, xor0)
    
    # Uncompute acc0 back to 0
    qc.x(acc0)
