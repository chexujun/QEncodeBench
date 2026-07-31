from qiskit import QuantumCircuit
from itertools import combinations

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,4), (0,5), (1,2), (1,3), (2,4), (2,5)]
    
    # Ancilla allocation
    edge_ancillas = ancilla_qubits[0:7]  # One per edge, = (NOT x_u) AND (NOT x_v) if not covered
    popcount_violation = ancilla_qubits[7]  # = 1 iff popcount > 4
    phase_qubit = ancilla_qubits[8]  # For applying global phase
    # ancilla_qubits[9] unused
    
    # Step 1: Compute for each edge whether it's NOT covered
    # edge_ancillas[i] = (NOT x_u) AND (NOT x_v) for edge (u, v)
    for i, (u, v) in enumerate(edges):
        # Prepare: flip both qubits to invert them
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        # MCX flips target if all controls are 1 (both inverted qubits)
        qc.mcx([problem_qubits[u], problem_qubits[v]], edge_ancillas[i])
        # Uncompute: flip back
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # Step 2: Check if popcount > 4
    # This means at least 5 of the 6 problem qubits are 1
    # For each combination of 5 qubits, if all are 1, set popcount_violation = 1
    for combo in combinations(range(6), 5):
        controls = [problem_qubits[i] for i in combo]
        qc.mcx(controls, popcount_violation)
    
    # Step 3: Apply phase -1 if (all edges are covered) AND (popcount <= 4)
    # This is equivalent to: apply phase -1 if (all edge_ancillas are 0) AND (popcount_violation is 0)
    
    # Prepare phase_qubit in |1⟩ state
    qc.x(phase_qubit)
    
    # Invert all ancillas so that predicate=true means all controls are |1⟩
    for anc in edge_ancillas + [popcount_violation]:
        qc.x(anc)
    
    # Apply multi-controlled Z using H-MCX-H conjugation
    # MCZ applies Z to target if all controls are |1⟩
    # Z|1⟩ = -|1⟩, giving global phase -1
    qc.h(phase_qubit)
    qc.mcx(edge_ancillas + [popcount_violation], phase_qubit)
    qc.h(phase_qubit)
    
    # Restore ancillas to original states
    for anc in reversed(edge_ancillas + [popcount_violation]):
        qc.x(anc)
    
    # Restore phase_qubit to |0⟩
    qc.x(phase_qubit)
    
    # Step 4: Uncompute in reverse order
    # Uncompute popcount_violation
    for combo in combinations(range(6), 5):
        controls = [problem_qubits[i] for i in combo]
        qc.mcx(controls, popcount_violation)
    
    # Uncompute edge_ancillas (mirror of compute)
    for i, (u, v) in enumerate(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.mcx([problem_qubits[u], problem_qubits[v]], edge_ancillas[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
