from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover phase oracle for 3-coloring of a 5-vertex graph.
    Marks states where all edges have endpoints of different colors.
    """
    edges = [(0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    
    result = ancilla_qubits[0]
    edge_temp = ancilla_qubits[1]
    and_temp = ancilla_qubits[2]
    aux_temp = ancilla_qubits[3]
    
    # Initialize result to |1>
    qc.x(result)
    
    # For each edge, compute whether colors differ and AND with accumulator
    for u, v in edges:
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        # Compute color_diff(u, v) into edge_temp
        compute_color_diff(qc, b0_u, b1_u, b0_v, b1_v, edge_temp, aux_temp)
        
        # AND result with edge_temp: result = result AND edge_temp
        qc.x(edge_temp)
        qc.ccx(result, edge_temp, and_temp)
        qc.cx(and_temp, result)
        qc.cx(and_temp, and_temp)
        qc.x(edge_temp)
        
        # Uncompute edge_temp
        uncomp_color_diff(qc, b0_u, b1_u, b0_v, b1_v, edge_temp, aux_temp)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute result
    qc.x(result)


def compute_color_diff(qc, b0_u, b1_u, b0_v, b1_v, output, aux):
    """
    Compute into output whether two 2-bit color codes differ (mod 3).
    Codes (b0, b1) map to colors: 00->0, 01->1, 10->2, 11->0.
    """
    # Colors are same iff: (both same bit patterns matching) OR (00 and 11) OR (11 and 00)
    # This is XOR of three mutually-exclusive terms:
    # term1: (b1_u == b1_v) AND (b0_u == b0_v)
    # term2: (NOT b0_u) AND (NOT b1_u) AND b0_v AND b1_v
    # term3: b0_u AND b1_u AND (NOT b0_v) AND (NOT b1_v)
    # different = NOT(term1 XOR term2 XOR term3)
    
    # Compute term1: (b1_u == b1_v) AND (b0_u == b0_v)
    # Use aux for intermediate XOR
    qc.cx(b1_u, aux)
    qc.cx(b1_v, aux)
    qc.x(aux)  # Now aux = (b1_u == b1_v)
    
    # Check (b0_u == b0_v) AND aux into output
    qc.cx(b0_u, output)
    qc.cx(b0_v, output)
    qc.x(output)  # output = (b0_u == b0_v)
    qc.ccx(output, aux, output)
    # Uncompute output prep
    qc.cx(b0_u, output)
    qc.cx(b0_v, output)
    # Now output = term1, aux still has (b1_u == b1_v)
    qc.x(aux)  # restore aux
    
    # Compute term2: (NOT b0_u) AND (NOT b1_u) AND b0_v AND b1_v
    qc.x(b0_u)
    qc.x(b1_u)
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    qc.x(b1_u)
    qc.x(b0_u)
    # XOR term2 into output
    qc.cx(aux, output)
    # Clear aux for term3
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    
    # Compute term3: b0_u AND b1_u AND (NOT b0_v) AND (NOT b1_v)
    qc.x(b0_v)
    qc.x(b1_v)
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    qc.x(b1_v)
    qc.x(b0_v)
    # XOR term3 into output
    qc.cx(aux, output)
    # Clear aux
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    
    # Negate output (output = NOT same = different)
    qc.x(output)


def uncomp_color_diff(qc, b0_u, b1_u, b0_v, b1_v, output, aux):
    """Reverse of compute_color_diff."""
    qc.x(output)  # undo final negation
    
    # Clear and reverse term3
    qc.x(b0_v)
    qc.x(b1_v)
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    qc.x(b1_v)
    qc.x(b0_v)
    qc.cx(aux, output)
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    
    # Reverse term2
    qc.x(b0_u)
    qc.x(b1_u)
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    qc.x(b1_u)
    qc.x(b0_u)
    qc.cx(aux, output)
    qc.mcp(math.pi, [b0_u, b1_u, b0_v, b1_v], aux)
    
    # Reverse term1
    qc.cx(b0_u, output)
    qc.cx(b0_v, output)
    qc.x(output)
    qc.cx(b1_u, aux)
    qc.cx(b1_v, aux)
    qc.x(aux)
    qc.ccx(output, aux, output)
    qc.cx(b0_u, output)
    qc.cx(b0_v, output)
    qc.x(aux)
    qc.cx(b1_u, aux)
    qc.cx(b1_v, aux)
