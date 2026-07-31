from qiskit import QuantumCircuit
from itertools import combinations

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,4), (0,5), (1,2), (1,3), (3,5)]
    
    # Compute edge coverage
    # ancilla_qubits[i] = 1 iff edge i is NOT covered (both endpoints = 0)
    for i, (u, v) in enumerate(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], ancilla_qubits[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # Compute size constraint
    # ancilla_qubits[6] = 1 iff popcount(problem_qubits) >= 4
    size_check = ancilla_qubits[6]
    for combo in combinations(range(6), 4):
        qubits_in_combo = [problem_qubits[i] for i in combo]
        qc.mcx(qubits_in_combo, size_check)
    
    # Flip to change interpretation: now ancilla[i]=1 means edge IS covered, size_check=1 means size <= 3
    for i in range(6):
        qc.x(ancilla_qubits[i])
    qc.x(size_check)
    
    # Apply phase if all conditions satisfied
    phase_target = ancilla_qubits[8]
    all_controls = ancilla_qubits[:7]
    qc.mcx(all_controls, phase_target)
    qc.z(phase_target)
    qc.mcx(all_controls, phase_target)
    
    # Uncompute (reverse order)
    qc.x(size_check)
    for i in range(6):
        qc.x(ancilla_qubits[i])
    
    for combo in reversed(list(combinations(range(6), 4))):
        qubits_in_combo = [problem_qubits[i] for i in combo]
        qc.mcx(qubits_in_combo, size_check)
    
    for i in range(len(edges)-1, -1, -1):
        u, v = edges[i]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], ancilla_qubits[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
