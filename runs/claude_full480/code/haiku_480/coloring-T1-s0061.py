from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for graph coloring: f(x) = 1 iff all edges connect different colors.
    Graph: 4 vertices, edges (0,3), (1,3), (2,3).
    Each vertex has 2-bit color code (surjective to 3 colors).
    """
    
    # Vertices and their color codes:
    # Vertex 0: bits [0,1], Vertex 1: bits [2,3], Vertex 2: bits [4,5], Vertex 3: bits [6,7]
    
    # Helper: compute (a XOR b) into target using CCX chains
    def compute_xor_into_target(qc, a, b, target):
        qc.cx(a, target)
        qc.cx(b, target)
    
    # Helper: compute OR(p, q) AND OR(r, s) into target
    # = (p XOR q XOR pq) AND (r XOR s XOR rs) where pq = p AND q, rs = r AND s
    # Expand: result = ((p XOR q) OR (pq)) AND ((r XOR s) OR (rs))
    def compute_colors_differ(qc, u0, u1, v0, v1, target, temp1, temp2, temp3):
        # p = u0 XOR v0, q = u1 XOR v1, r = u0 XOR u1, s = v0 XOR v1
        # result = (p OR q) AND (r OR s)
        # Expand: = (p AND r) OR (p AND s) OR (q AND r) OR (q AND s)
        
        # Compute (u0 XOR v0) AND (u0 XOR u1) into temp1
        # This is true iff (u0!=v0) AND (u0!=u1)
        # = (u0=0,v0=1,u1=1) OR (u0=1,v0=0,u1=0)
        qc.cx(v0, temp1)
        qc.cx(u0, temp1)
        qc.cx(u1, temp1)
        qc.x(u0)
        qc.x(u1)
        qc.ccx(u0, u1, temp1)
        qc.x(u0)
        qc.x(u1)
        
        # Compute (u0 XOR v0) AND (v0 XOR v1) into temp2
        qc.cx(u0, temp2)
        qc.cx(v0, temp2)
        qc.cx(v1, temp2)
        qc.x(v0)
        qc.x(v1)
        qc.ccx(v0, v1, temp2)
        qc.x(v0)
        qc.x(v1)
        
        # OR temp1 and temp2 into target
        qc.cx(temp1, target)
        qc.cx(temp2, target)
    
    # For each edge, compute if colors differ
    # Use ancilla_qubits[0,1,2] for the three edges, [3] for final AND
    
    # Edge (0,3): vertices 0 and 3
    u0, u1 = problem_qubits[0], problem_qubits[1]
    v0, v1 = problem_qubits[6], problem_qubits[7]
    # Direct computation for this edge using controlled gates
    qc.cx(u0, ancilla_qubits[0])
    qc.cx(v0, ancilla_qubits[0])
    qc.cx(u1, ancilla_qubits[0])
    qc.cx(v1, ancilla_qubits[0])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.mcp(3.14159265359, [u0, u1, v0, v1], ancilla_qubits[0])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.cx(u0, ancilla_qubits[0])
    qc.cx(v0, ancilla_qubits[0])
    qc.cx(u1, ancilla_qubits[0])
    qc.cx(v1, ancilla_qubits[0])
    
    # Edge (1,3): vertices 1 and 3
    u0, u1 = problem_qubits[2], problem_qubits[3]
    v0, v1 = problem_qubits[6], problem_qubits[7]
    qc.cx(u0, ancilla_qubits[1])
    qc.cx(v0, ancilla_qubits[1])
    qc.cx(u1, ancilla_qubits[1])
    qc.cx(v1, ancilla_qubits[1])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.mcp(3.14159265359, [u0, u1, v0, v1], ancilla_qubits[1])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.cx(u0, ancilla_qubits[1])
    qc.cx(v0, ancilla_qubits[1])
    qc.cx(u1, ancilla_qubits[1])
    qc.cx(v1, ancilla_qubits[1])
    
    # Edge (2,3): vertices 2 and 3
    u0, u1 = problem_qubits[4], problem_qubits[5]
    v0, v1 = problem_qubits[6], problem_qubits[7]
    qc.cx(u0, ancilla_qubits[2])
    qc.cx(v0, ancilla_qubits[2])
    qc.cx(u1, ancilla_qubits[2])
    qc.cx(v1, ancilla_qubits[2])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.mcp(3.14159265359, [u0, u1, v0, v1], ancilla_qubits[2])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.cx(u0, ancilla_qubits[2])
    qc.cx(v0, ancilla_qubits[2])
    qc.cx(u1, ancilla_qubits[2])
    qc.cx(v1, ancilla_qubits[2])
    
    # AND all three together and apply phase
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[3])
    qc.ccx(ancilla_qubits[3], ancilla_qubits[2], ancilla_qubits[3])
    qc.z(ancilla_qubits[3])
    qc.ccx(ancilla_qubits[3], ancilla_qubits[2], ancilla_qubits[3])
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[3])
    
    # Uncompute ancillas [0,1,2]
    u0, u1 = problem_qubits[4], problem_qubits[5]
    v0, v1 = problem_qubits[6], problem_qubits[7]
    qc.cx(u0, ancilla_qubits[2])
    qc.cx(v0, ancilla_qubits[2])
    qc.cx(u1, ancilla_qubits[2])
    qc.cx(v1, ancilla_qubits[2])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.mcp(3.14159265359, [u0, u1, v0, v1], ancilla_qubits[2])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.cx(u0, ancilla_qubits[2])
    qc.cx(v0, ancilla_qubits[2])
    qc.cx(u1, ancilla_qubits[2])
    qc.cx(v1, ancilla_qubits[2])
    
    u0, u1 = problem_qubits[2], problem_qubits[3]
    v0, v1 = problem_qubits[6], problem_qubits[7]
    qc.cx(u0, ancilla_qubits[1])
    qc.cx(v0, ancilla_qubits[1])
    qc.cx(u1, ancilla_qubits[1])
    qc.cx(v1, ancilla_qubits[1])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.mcp(3.14159265359, [u0, u1, v0, v1], ancilla_qubits[1])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.cx(u0, ancilla_qubits[1])
    qc.cx(v0, ancilla_qubits[1])
    qc.cx(u1, ancilla_qubits[1])
    qc.cx(v1, ancilla_qubits[1])
    
    u0, u1 = problem_qubits[0], problem_qubits[1]
    v0, v1 = problem_qubits[6], problem_qubits[7]
    qc.cx(u0, ancilla_qubits[0])
    qc.cx(v0, ancilla_qubits[0])
    qc.cx(u1, ancilla_qubits[0])
    qc.cx(v1, ancilla_qubits[0])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.mcp(3.14159265359, [u0, u1, v0, v1], ancilla_qubits[0])
    qc.x(u0)
    qc.x(u1)
    qc.x(v0)
    qc.x(v1)
    qc.cx(u0, ancilla_qubits[0])
    qc.cx(v0, ancilla_qubits[0])
    qc.cx(u1, ancilla_qubits[0])
    qc.cx(v1, ancilla_qubits[0])
