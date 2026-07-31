from qiskit import QuantumCircuit
from qiskit.circuit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover phase oracle for graph 5-coloring with 3 colors.
    Marks states where all edges have endpoints of different colors.
    
    Color decoding (per vertex v with bits b0=problem_qubits[2v], b1=problem_qubits[2v+1]):
    - Code 00 (0): color 0
    - Code 01 (1): color 1
    - Code 10 (2): color 2
    - Code 11 (3): color 0
    
    Two vertices have the same color iff:
    - Same code, OR
    - Codes are 00 and 11 (both map to color 0)
    """
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 4), (3, 4)]
    
    result = ancilla_qubits[0]  # Will hold: 1 if all edges valid, 0 if any invalid
    qc.x(result)  # Initialize to |1>
    
    for u, v in edges:
        u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u + 1]
        v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        # Compute into ancilla_qubits[1] whether this edge has same color
        same_color = ancilla_qubits[1]
        
        # Compute b0_xor = b0_u XOR b0_v
        qc.cx(u_b0, ancilla_qubits[2])
        qc.cx(v_b0, ancilla_qubits[2])
        
        # Compute b1_xor = b1_u XOR b1_v  
        qc.cx(u_b1, ancilla_qubits[3])
        qc.cx(v_b1, ancilla_qubits[3])
        
        # same_color = 1 if:
        # (NOT b0_xor AND NOT b1_xor) OR (b0_xor AND b1_xor AND NOT(b0_u XOR b1_u))
        
        # Compute NOT b0_xor AND NOT b1_xor into same_color
        qc.x(ancilla_qubits[2])
        qc.x(ancilla_qubits[3])
        qc.mcx([ancilla_qubits[2], ancilla_qubits[3]], same_color)
        qc.x(ancilla_qubits[2])
        qc.x(ancilla_qubits[3])
        
        # Compute b0_u XOR b1_u into temp
        qc.cx(u_b0, ancilla_qubits[2])
        qc.cx(u_b1, ancilla_qubits[2])
        
        # Compute b0_xor AND b1_xor AND NOT(b0_u XOR b1_u) and OR with same_color
        qc.x(ancilla_qubits[2])
        qc.mcx([ancilla_qubits[1], ancilla_qubits[3], ancilla_qubits[2]], same_color)
        qc.x(ancilla_qubits[2])
        
        # Apply AND operation: result = result AND NOT same_color
        # result' = result XOR (result AND same_color)
        temp_and = ancilla_qubits[2]
        qc.mcx([result, same_color], temp_and)
        qc.cx(temp_and, result)
        qc.mcx([result, same_color], temp_and)
        
        # Uncompute same_color
        qc.x(ancilla_qubits[2])
        qc.mcx([same_color, ancilla_qubits[3], ancilla_qubits[2]], ancilla_qubits[1])
        qc.x(ancilla_qubits[2])
        
        qc.cx(u_b1, ancilla_qubits[2])
        qc.cx(u_b0, ancilla_qubits[2])
        
        qc.x(ancilla_qubits[2])
        qc.x(ancilla_qubits[3])
        qc.mcx([ancilla_qubits[2], ancilla_qubits[3]], ancilla_qubits[1])
        qc.x(ancilla_qubits[2])
        qc.x(ancilla_qubits[3])
        
        qc.cx(v_b1, ancilla_qubits[3])
        qc.cx(u_b1, ancilla_qubits[3])
        
        qc.cx(v_b0, ancilla_qubits[2])
        qc.cx(u_b0, ancilla_qubits[2])
    
    # Apply phase -1 when result == 1 (all edges valid)
    qc.z(result)
    
    # Uncompute result and the entire loop in reverse
    for u, v in reversed(edges):
        u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u + 1]
        v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.cx(u_b0, ancilla_qubits[2])
        qc.cx(v_b0, ancilla_qubits[2])
        
        qc.cx(u_b1, ancilla_qubits[3])
        qc.cx(v_b1, ancilla_qubits[3])
        
        qc.x(ancilla_qubits[2])
        qc.x(ancilla_qubits[3])
        qc.mcx([ancilla_qubits[2], ancilla_qubits[3]], ancilla_qubits[1])
        qc.x(ancilla_qubits[2])
        qc.x(ancilla_qubits[3])
        
        qc.cx(u_b0, ancilla_qubits[2])
        qc.cx(u_b1, ancilla_qubits[2])
        
        qc.x(ancilla_qubits[2])
        qc.mcx([ancilla_qubits[1], ancilla_qubits[3], ancilla_qubits[2]], ancilla_qubits[1])
        qc.x(ancilla_qubits[2])
        
        qc.cx(u_b1, ancilla_qubits[2])
        qc.cx(u_b0, ancilla_qubits[2])
        
        temp_and = ancilla_qubits[2]
        qc.mcx([result, ancilla_qubits[1]], temp_and)
        qc.cx(temp_and, result)
        qc.mcx([result, ancilla_qubits[1]], temp_and)
        
        qc.x(ancilla_qubits[3])
        qc.cx(v_b1, ancilla_qubits[3])
        qc.cx(u_b1, ancilla_qubits[3])
        
        qc.x(ancilla_qubits[2])
        qc.cx(v_b0, ancilla_qubits[2])
        qc.cx(u_b0, ancilla_qubits[2])
    
    qc.x(result)
