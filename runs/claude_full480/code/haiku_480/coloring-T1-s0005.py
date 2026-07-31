from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (2, 4), (3, 4)]
    
    edge_validity = ancilla_qubits[:4]
    final_result = ancilla_qubits[4]
    
    # Compute edge validity flags
    for idx, (u, v) in enumerate(edges):
        compute_edge_valid(qc, problem_qubits, edge_validity[idx], u, v)
    
    # AND all flags into final_result
    qc.x(final_result)
    for flag in edge_validity:
        qc.x(flag)
        qc.mcx([flag, final_result], final_result)
        qc.x(flag)
    
    # Apply phase -1 if all edges valid
    qc.p(math.pi, final_result)
    
    # Uncompute AND
    for flag in edge_validity:
        qc.x(flag)
        qc.mcx([flag, final_result], final_result)
        qc.x(flag)
    qc.x(final_result)
    
    # Uncompute edge validities (reverse order)
    for idx in range(len(edges) - 1, -1, -1):
        uncompute_edge_valid(qc, problem_qubits, edge_validity[idx],
                            edges[idx][0], edges[idx][1])


def compute_edge_valid(qc, problem_qubits, flag, u, v):
    """Compute flag=1 if edge (u,v) has different colors, 0 if same color."""
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u + 1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v + 1]
    
    qc.x(flag)
    
    # Colors are same when: (c_u % 3) == (c_v % 3)
    # This occurs for states: (0,0,0,0), (0,1,0,1), (1,0,1,0), (1,1,0,0), (1,1,1,1)
    same_color_states = [
        (False, False, False, False),
        (False, True, False, True),
        (True, False, True, False),
        (True, True, False, False),
        (True, True, True, True),
    ]
    
    qubits = [b1_u, b0_u, b1_v, b0_v]
    
    for state in same_color_states:
        # Apply X gates to negate qubits where state bit is 0
        for qubit, bit_value in zip(qubits, state):
            if not bit_value:
                qc.x(qubit)
        # Flip flag if all qubits match the state
        qc.mcx(qubits, flag)
        # Restore X gates
        for qubit, bit_value in zip(qubits, state):
            if not bit_value:
                qc.x(qubit)


def uncompute_edge_valid(qc, problem_qubits, flag, u, v):
    """Mirror of compute_edge_valid."""
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u + 1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v + 1]
    
    same_color_states = [
        (True, True, True, True),
        (True, True, False, False),
        (True, False, True, False),
        (False, True, False, True),
        (False, False, False, False),
    ]
    
    qubits = [b1_u, b0_u, b1_v, b0_v]
    
    for state in same_color_states:
        for qubit, bit_value in zip(qubits, state):
            if not bit_value:
                qc.x(qubit)
        qc.mcx(qubits, flag)
        for qubit, bit_value in zip(qubits, state):
            if not bit_value:
                qc.x(qubit)
    
    qc.x(flag)
