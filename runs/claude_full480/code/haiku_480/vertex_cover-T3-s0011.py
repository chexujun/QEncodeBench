from qiskit import QuantumCircuit
from itertools import combinations

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,3), (0,4), (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (3,5), (4,5)]
    
    edges_ok = ancilla_qubits[0]
    card_ok = ancilla_qubits[1]
    is_valid = ancilla_qubits[2]
    temp = ancilla_qubits[3]
    temp2 = ancilla_qubits[4]
    temp3 = ancilla_qubits[5]
    
    # COMPUTE PHASE
    qc.x(edges_ok)
    
    for u, v in edges:
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], temp)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
        qc.cx(temp, edges_ok)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], temp)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    qc.x(card_ok)
    
    combos = list(combinations(range(6), 4))
    for combo in combos:
        a, b, c, d = combo
        
        qc.ccx(problem_qubits[a], problem_qubits[b], temp)
        qc.ccx(temp, problem_qubits[c], temp2)
        qc.ccx(temp2, problem_qubits[d], temp3)
        qc.cx(temp3, card_ok)
        qc.ccx(temp2, problem_qubits[d], temp3)
        qc.ccx(temp, problem_qubits[c], temp2)
        qc.ccx(problem_qubits[a], problem_qubits[b], temp)
    
    qc.ccx(edges_ok, card_ok, is_valid)
    
    # APPLY PHASE
    qc.z(is_valid)
    
    # UNCOMPUTE PHASE
    qc.ccx(edges_ok, card_ok, is_valid)
    
    for combo in reversed(combos):
        a, b, c, d = combo
        
        qc.ccx(problem_qubits[a], problem_qubits[b], temp)
        qc.ccx(temp, problem_qubits[c], temp2)
        qc.ccx(temp2, problem_qubits[d], temp3)
        qc.cx(temp3, card_ok)
        qc.ccx(temp2, problem_qubits[d], temp3)
        qc.ccx(temp, problem_qubits[c], temp2)
        qc.ccx(problem_qubits[a], problem_qubits[b], temp)
    
    qc.x(card_ok)
    
    for u, v in reversed(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], temp)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
        qc.cx(temp, edges_ok)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], temp)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    qc.x(edges_ok)
