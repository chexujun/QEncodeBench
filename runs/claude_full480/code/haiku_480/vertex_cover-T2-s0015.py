from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Valid vertex covers of size 3 for the given graph.
    # These are the only sets of 3 vertices covering all 5 edges:
    # edges = [(0,2), (1,3), (1,4), (2,3), (3,4)]
    valid_states = [
        (0, 1, 0, 1, 1),  # vertices {0, 1, 3}
        (1, 0, 0, 1, 1),  # vertices {0, 3, 4}
        (0, 1, 1, 1, 0),  # vertices {1, 2, 3}
        (1, 0, 1, 1, 0),  # vertices {1, 2, 4}
        (1, 1, 1, 0, 0),  # vertices {2, 3, 4}
    ]
    
    # For each valid state, mark it with phase -1 using compute-phase-uncompute
    for state in valid_states:
        # Flip qubits that are 0 in the target state so all become 1
        for i in range(5):
            if state[i] == 0:
                qc.x(x[i])
        
        # Compute AND of all problem qubits into ancilla chain a[0..3]
        # After this, a[3] = AND(x[0], x[1], x[2], x[3], x[4]) = 1
        qc.ccx(x[0], x[1], a[0])
        qc.ccx(a[0], x[2], a[1])
        qc.ccx(a[1], x[3], a[2])
        qc.ccx(a[2], x[4], a[3])
        
        # Apply phase -1 when all bits are 1 (i.e., input matches state)
        qc.z(a[3])
        
        # Uncompute: reverse the AND chain to restore ancillas to |0>
        qc.ccx(a[2], x[4], a[3])
        qc.ccx(a[1], x[3], a[2])
        qc.ccx(a[0], x[2], a[1])
        qc.ccx(x[0], x[1], a[0])
        
        # Restore problem qubits to original state
        for i in range(5):
            if state[i] == 0:
                qc.x(x[i])
