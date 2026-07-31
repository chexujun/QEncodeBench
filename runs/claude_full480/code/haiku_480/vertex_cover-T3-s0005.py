from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [(0,2), (0,3), (0,4), (0,5), (1,3), (1,5), (2,3), (2,5), (3,4), (4,5)]
    
    edge_anc = ancilla_qubits[0:10]
    popcount_anc = ancilla_qubits[10:13]
    
    # Compute edges 0-5 into edge_anc[0:6]
    for i in range(6):
        u, v = edges[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_anc[i])
        qc.cx(problem_qubits[u], edge_anc[i])
        qc.cx(problem_qubits[v], edge_anc[i])
    
    # Compute popcount into popcount_anc[0:3] using edge_anc[6:9] as carry storage
    for qubit in problem_qubits:
        qc.ccx(popcount_anc[0], qubit, edge_anc[6])
        qc.ccx(popcount_anc[1], edge_anc[6], edge_anc[7])
        qc.ccx(popcount_anc[2], edge_anc[7], edge_anc[8])
        qc.cx(qubit, popcount_anc[0])
        qc.cx(edge_anc[6], popcount_anc[1])
        qc.cx(edge_anc[7], popcount_anc[2])
    
    # Compute edges 6-9 into edge_anc[6:10]
    for i in range(6, 10):
        u, v = edges[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_anc[i])
        qc.cx(problem_qubits[u], edge_anc[i])
        qc.cx(problem_qubits[v], edge_anc[i])
    
    # Apply phase: Z controlled by all edges AND (popcount_anc[2] == 0)
    # Flip popcount_anc[2] to check when it's 0
    qc.x(popcount_anc[2])
    # Multi-controlled P(pi) = multi-controlled Z
    qc.mcp(np.pi, edge_anc[0:10] + [popcount_anc[2]], popcount_anc[2])
    qc.x(popcount_anc[2])
    
    # Uncompute edges 6-9
    for i in range(9, 5, -1):
        u, v = edges[i]
        qc.cx(problem_qubits[v], edge_anc[i])
        qc.cx(problem_qubits[u], edge_anc[i])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_anc[i])
    
    # Uncompute popcount (reverse order)
    for qubit in reversed(problem_qubits):
        qc.cx(edge_anc[7], popcount_anc[2])
        qc.cx(edge_anc[6], popcount_anc[1])
        qc.cx(qubit, popcount_anc[0])
        qc.ccx(popcount_anc[2], edge_anc[7], edge_anc[8])
        qc.ccx(popcount_anc[1], edge_anc[6], edge_anc[7])
        qc.ccx(popcount_anc[0], qubit, edge_anc[6])
    
    # Uncompute edges 0-5
    for i in range(5, -1, -1):
        u, v = edges[i]
        qc.cx(problem_qubits[v], edge_anc[i])
        qc.cx(problem_qubits[u], edge_anc[i])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_anc[i])
