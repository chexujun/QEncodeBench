from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    # Vertices: 0→[0,1], 1→[2,3], 2→[4,5], 3→[6,7]
    # Edges: (0,2), (1,3), (2,3)
    # Predicate: different_color(u,v) = (p_u XOR p_v) OR (p_u AND (b0_u XOR b0_v))
    # where p = b0 XOR b1
    
    # Compute edge (0,2) predicate into a[0]
    _compute_edge_pred(qc, problem_qubits, ancilla_qubits, 0, 2)
    
    # Compute edge (1,3) predicate into a[1]
    _compute_edge_pred(qc, problem_qubits, ancilla_qubits, 1, 3)
    
    # Compute edge (2,3) predicate into a[2]
    _compute_edge_pred(qc, problem_qubits, ancilla_qubits, 2, 3)
    
    # Combine with AND: a[3] = a[0] AND a[1]
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[3])
    
    # Reuse a[1]: a[1] = a[3] AND a[2]
    qc.ccx(ancilla_qubits[3], ancilla_qubits[2], ancilla_qubits[1])
    
    # Apply phase to a[1]
    qc.z(ancilla_qubits[1])
    
    # Uncompute AND operations
    qc.ccx(ancilla_qubits[3], ancilla_qubits[2], ancilla_qubits[1])
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[3])
    
    # Uncompute edge predicates (reverse order)
    _uncompute_edge_pred(qc, problem_qubits, ancilla_qubits, 2, 3)
    _uncompute_edge_pred(qc, problem_qubits, ancilla_qubits, 1, 3)
    _uncompute_edge_pred(qc, problem_qubits, ancilla_qubits, 0, 2)


def _compute_edge_pred(qc, problem_qubits, ancilla_qubits, u, v):
    """Compute different_color(u,v) into ancilla_qubits[u//2] using formula:
    (p_u XOR p_v) OR (p_u AND (b0_u XOR b0_v)) where p = b0 XOR b1"""
    
    q_u_low = problem_qubits[2*u]
    q_u_high = problem_qubits[2*u + 1]
    q_v_low = problem_qubits[2*v]
    q_v_high = problem_qubits[2*v + 1]
    
    result = ancilla_qubits[u] if u < 3 else ancilla_qubits[0]
    
    # Use remaining ancillas as temp storage
    temp = [ancilla_qubits[i] for i in range(4) if i != u and i != (u if u < 3 else 0)]
    
    # Compute p_u = q_u_low XOR q_u_high into temp[0]
    qc.cx(q_u_high, temp[0])
    qc.cx(q_u_low, temp[0])
    
    # Compute p_v = q_v_low XOR q_v_high into temp[1]
    qc.cx(q_v_high, temp[1])
    qc.cx(q_v_low, temp[1])
    
    # Compute (q_u_low XOR q_v_low) into temp[2]
    qc.cx(q_u_low, temp[2])
    qc.cx(q_v_low, temp[2])
    
    # Compute (p_u XOR p_v) into result
    qc.cx(temp[0], result)
    qc.cx(temp[1], result)
    
    # Compute (p_u AND (b0_u XOR b0_v)) into temp[1], then OR with result
    qc.ccx(temp[0], temp[2], temp[1])
    
    # OR: result = result OR temp[1]
    # Using: A OR B = NOT(NOT A AND NOT B) = NOT((1-A)(1-B)) = A + B - A*B
    # Simpler: flip, AND, flip
    qc.x(result)
    qc.x(temp[1])
    qc.ccx(result, temp[1], temp[0])
    qc.x(result)
    qc.x(temp[1])
    qc.x(temp[0])
    qc.cx(temp[0], result)
    
    # Clean up temp ancillas
    qc.ccx(temp[0], temp[2], temp[1])
    qc.cx(q_u_low, temp[2])
    qc.cx(q_v_low, temp[2])
    qc.cx(q_v_high, temp[1])
    qc.cx(q_v_low, temp[1])
    qc.cx(q_u_high, temp[0])
    qc.cx(q_u_low, temp[0])


def _uncompute_edge_pred(qc, problem_qubits, ancilla_qubits, u, v):
    """Reverse of _compute_edge_pred"""
    _compute_edge_pred(qc, problem_qubits, ancilla_qubits, u, v)
