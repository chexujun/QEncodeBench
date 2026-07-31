from qiskit import QuantumCircuit
from itertools import combinations

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (1,5), (2,3), (2,4), (3,4), (3,5), (4,5)]
    
    result = ancilla_qubits[0]
    edge_flags = ancilla_qubits[1:8]
    helper1 = ancilla_qubits[8]
    helper2 = ancilla_qubits[9]
    
    # --- COMPUTE PHASE ---
    
    # Step 1: Compute coverage flag for each edge
    # Edge (i,j) is covered iff x_i OR x_j = 1
    for idx, (i, j) in enumerate(edges):
        f = edge_flags[idx]
        qc.cx(problem_qubits[i], f)
        qc.cx(problem_qubits[j], f)
        qc.ccx(problem_qubits[i], problem_qubits[j], f)
        # f = x_i XOR x_j XOR (x_i AND x_j) = x_i OR x_j
    
    # Step 2: AND all edge coverage flags into result
    qc.mcx(edge_flags, result)
    # result = AND(all edge_covered)
    
    # Step 3: AND with (popcount <= 3) constraint
    # popcount >= 4 iff some 4-subset has all bits set to 1
    # So: popcount <= 3 iff NOT(exists 4-subset with all 1s)
    subsets_4 = list(combinations(range(6), 4))
    
    for subset in subsets_4:
        subset_qubits = [problem_qubits[i] for i in subset]
        
        # Compute: helper1 = AND(subset_qubits)
        qc.mcx(subset_qubits, helper1)
        
        # AND constraint into result: result = result AND NOT(helper1)
        # Implement: result ^= result AND helper1 (flips result to 0 if both are 1)
        qc.ccx(result, helper1, helper2)
        qc.cx(helper2, result)
        
        # Uncompute helper2 and helper1
        qc.ccx(result, helper1, helper2)
        qc.mcx(subset_qubits, helper1)
    
    # --- PHASE STEP ---
    qc.z(result)
    
    # --- UNCOMPUTE PHASE ---
    
    # Reverse Step 2: AND of edge flags
    qc.mcx(edge_flags, result)
    
    # Reverse Step 1: edge coverage flags
    for idx in range(len(edges) - 1, -1, -1):
        i, j = edges[idx]
        f = edge_flags[idx]
        qc.ccx(problem_qubits[i], problem_qubits[j], f)
        qc.cx(problem_qubits[j], f)
        qc.cx(problem_qubits[i], f)
