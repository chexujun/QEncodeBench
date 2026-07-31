import numpy as np
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (1, 3)]
    
    # Compute same_color for each edge into ancilla[0:3]
    for idx, (u, v) in enumerate(edges):
        compute_same_color_edge(qc, problem_qubits, u, v, ancilla_qubits[idx])
    
    # Apply phase if all edges are different (all same_color bits are 0)
    # Use X gates to negate controls, then mcp to apply phase
    qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1])
    qc.x(ancilla_qubits[2])
    qc.mcp(np.pi, [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]], ancilla_qubits[3])
    qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1])
    qc.x(ancilla_qubits[2])
    
    # Uncompute same_color bits
    for idx in reversed(range(len(edges))):
        u, v = edges[idx]
        uncompute_same_color_edge(qc, problem_qubits, u, v, ancilla_qubits[idx])

def compute_same_color_edge(qc, problem_qubits, u, v, result):
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u+1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v+1]
    
    # Six cases where colors are the same
    conditions = [
        ([b0_u, b1_u, b0_v, b1_v], [True, True, True, True]),    # (0,0) vs (0,0)
        ([b0_u, b1_u, b0_v, b1_v], [True, True, False, False]),   # (0,0) vs (1,1)
        ([b0_u, b1_u, b0_v, b1_v], [False, True, False, True]),   # (1,0) vs (1,0)
        ([b0_u, b1_u, b0_v, b1_v], [True, False, True, False]),   # (0,1) vs (0,1)
        ([b0_u, b1_u, b0_v, b1_v], [False, False, True, True]),   # (1,1) vs (0,0)
        ([b0_u, b1_u, b0_v, b1_v], [False, False, False, False]), # (1,1) vs (1,1)
    ]
    
    for qubits, negate_flags in conditions:
        for q, negate in zip(qubits, negate_flags):
            if negate:
                qc.x(q)
        qc.mcx(qubits, result)
        for q, negate in zip(qubits, negate_flags):
            if negate:
                qc.x(q)

def uncompute_same_color_edge(qc, problem_qubits, u, v, result):
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u+1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v+1]
    
    conditions = [
        ([b0_u, b1_u, b0_v, b1_v], [True, True, True, True]),
        ([b0_u, b1_u, b0_v, b1_v], [True, True, False, False]),
        ([b0_u, b1_u, b0_v, b1_v], [False, True, False, True]),
        ([b0_u, b1_u, b0_v, b1_v], [True, False, True, False]),
        ([b0_u, b1_u, b0_v, b1_v], [False, False, True, True]),
        ([b0_u, b1_u, b0_v, b1_v], [False, False, False, False]),
    ]
    
    for qubits, negate_flags in reversed(conditions):
        for q, negate in zip(qubits, negate_flags):
            if negate:
                qc.x(q)
        qc.mcx(qubits, result)
        for q, negate in zip(qubits, negate_flags):
            if negate:
                qc.x(q)
