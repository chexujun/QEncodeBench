from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,3), (0,4), (1,3), (1,4), (2,3)]
    
    edge_uncovered = ancilla_qubits[0:6]
    any_uncovered = ancilla_qubits[6]
    popcount_ge4 = ancilla_qubits[7]
    temp_phase = ancilla_qubits[8]
    
    # COMPUTE: for each edge, flag if it is uncovered (both endpoints absent)
    for i, (u, v) in enumerate(edges):
        qc.x(edge_uncovered[i])
        qc.cx(problem_qubits[u], edge_uncovered[i])
        qc.cx(problem_qubits[v], edge_uncovered[i])
    
    # COMPUTE: any_uncovered = OR of all edge_uncovered flags
    for e in edge_uncovered:
        qc.cx(e, any_uncovered)
    
    # COMPUTE: popcount_ge4 flag (all 4-subsets and full 5-set)
    for combo in [[0,1,2,3], [0,1,2,4], [0,1,3,4], [0,2,3,4], [1,2,3,4], [0,1,2,3,4]]:
        controls = [problem_qubits[i] for i in combo]
        qc.append(MCXGate(len(combo)), controls + [popcount_ge4])
    
    # PHASE: apply -1 iff (all edges covered AND popcount <= 3)
    qc.x(any_uncovered)
    qc.x(popcount_ge4)
    qc.ccx(any_uncovered, popcount_ge4, temp_phase)
    qc.z(temp_phase)
    qc.ccx(any_uncovered, popcount_ge4, temp_phase)
    qc.x(popcount_ge4)
    qc.x(any_uncovered)
    
    # UNCOMPUTE: popcount_ge4
    for combo in reversed([[0,1,2,3], [0,1,2,4], [0,1,3,4], [0,2,3,4], [1,2,3,4], [0,1,2,3,4]]):
        controls = [problem_qubits[i] for i in combo]
        qc.append(MCXGate(len(combo)), controls + [popcount_ge4])
    
    # UNCOMPUTE: any_uncovered
    for e in reversed(edge_uncovered):
        qc.cx(e, any_uncovered)
    
    # UNCOMPUTE: edge_uncovered flags
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        qc.cx(problem_qubits[v], edge_uncovered[i])
        qc.cx(problem_qubits[u], edge_uncovered[i])
        qc.x(edge_uncovered[i])
