from qiskit import QuantumCircuit
from itertools import combinations

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,3), (0,5), (2,3), (2,4), (3,5), (4,5)]
    
    # Ancilla allocation
    edge_or = ancilla_qubits[0:8]        # edge_or[i] = problem_qubits[u] OR problem_qubits[v] for edge i
    edges_ok = ancilla_qubits[8]        # 1 iff all edges covered
    popcount_ok = ancilla_qubits[9]     # 1 iff popcount <= 4
    solution = ancilla_qubits[10]       # 1 iff valid solution
    
    # Compute OR for each edge: edge_or[i] = problem_qubits[u] OR problem_qubits[v]
    # Using: OR = NOT(NOT a AND NOT b)
    for i, (u, v) in enumerate(edges):
        qc.x(edge_or[i])                          # Initialize to 1
        qc.x(problem_qubits[u])                   # Flip to get NOT u
        qc.x(problem_qubits[v])                   # Flip to get NOT v
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_or[i])  # If both NOT u and NOT v, flip result
        qc.x(problem_qubits[v])                   # Restore v
        qc.x(problem_qubits[u])                   # Restore u
    
    # Compute edges_ok = AND of all edge_or values
    # edges_ok = 1 iff all edges are covered
    qc.x(edges_ok)                           # Initialize to 1
    qc.mcx(list(edge_or), edges_ok)          # Flip if any edge is uncovered (mcx flips if all controls=1, so we're checking all=1)
    
    # Compute popcount_ok = 1 iff popcount(problem_qubits) <= 4
    # Equivalently, popcount_ok = 1 iff popcount NOT in {5, 6}
    # We flip popcount_ok for each bad subset (size 5 or 6) that is all 1s
    # If 0 or even number of bad subsets all-1: popcount_ok stays 1
    # If odd number (1 or 7): popcount_ok becomes 0
    # Since only one popcount value per input state, either 0 or 1 bad subset can be all-1s
    qc.x(popcount_ok)                         # Initialize to 1
    for subset in list(combinations(range(6), 5)) + [tuple(range(6))]:
        qc.mcx([problem_qubits[i] for i in subset], popcount_ok)
    
    # Compute solution = edges_ok AND popcount_ok
    qc.x(solution)                            # Initialize to 1
    qc.ccx(edges_ok, popcount_ok, solution)   # Flip if any condition fails
    
    # Apply phase: Z gate flips phase if ancilla is 1
    qc.z(solution)
    
    # Uncompute solution
    qc.ccx(edges_ok, popcount_ok, solution)
    qc.x(solution)
    
    # Uncompute popcount_ok
    for subset in reversed(list(combinations(range(6), 5)) + [tuple(range(6))]):
        qc.mcx([problem_qubits[i] for i in subset], popcount_ok)
    qc.x(popcount_ok)
    
    # Uncompute edges_ok
    qc.mcx(list(edge_or), edges_ok)
    qc.x(edges_ok)
    
    # Uncompute edge OR values
    for i, (u, v) in reversed(list(enumerate(edges))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_or[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
        qc.x(edge_or[i])
