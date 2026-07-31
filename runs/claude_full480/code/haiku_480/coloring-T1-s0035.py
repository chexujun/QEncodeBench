from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Graph coloring oracle for 4 vertices with edges (0,1), (1,2), (2,3).
    Each vertex uses 2 qubits: low bit and high bit.
    Color mapping: 2-bit code c → color (c mod 3).
    Oracle applies phase -1 iff all edges have endpoints with different colors.
    """
    
    def compute_different_color(u0, u1, v0, v1, output):
        """
        Compute 1 iff vertices (u1,u0) and (v1,v0) have different colors into output.
        Colors are the same for: (00,00), (00,11), (01,01), (10,10), (11,00), (11,11).
        """
        # Apply multi-controlled X for each "same_color" case, then negate result
        
        # Case (00, 00): all bits are 0
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v1)
        qc.x(v0)
        qc.x(u1)
        qc.x(u0)
        
        # Case (00, 11): u0=0, u1=0, v0=1, v1=1
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(u1)
        qc.x(u0)
        
        # Case (01, 01): u0=1, u1=0, v0=1, v1=0
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v1)
        qc.x(u1)
        
        # Case (10, 10): u0=0, u1=1, v0=0, v1=1
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v0)
        qc.x(u0)
        
        # Case (11, 00): u0=1, u1=1, v0=0, v1=0
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v1)
        qc.x(v0)
        
        # Case (11, 11): all bits are 1
        qc.mcx([u0, u1, v0, v1], output)
        
        # Negate to get different_color
        qc.x(output)
    
    def uncompute_different_color(u0, u1, v0, v1, output):
        """Reverse of compute_different_color."""
        qc.x(output)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v1)
        qc.x(v0)
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v0)
        qc.x(u0)
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v1)
        qc.x(u1)
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(u1)
        qc.x(u0)
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], output)
        qc.x(v1)
        qc.x(v0)
        qc.x(u1)
        qc.x(u0)
    
    # Compute whether each edge constraint is satisfied
    compute_different_color(problem_qubits[0], problem_qubits[1],
                           problem_qubits[2], problem_qubits[3],
                           ancilla_qubits[0])
    compute_different_color(problem_qubits[2], problem_qubits[3],
                           problem_qubits[4], problem_qubits[5],
                           ancilla_qubits[1])
    compute_different_color(problem_qubits[4], problem_qubits[5],
                           problem_qubits[6], problem_qubits[7],
                           ancilla_qubits[2])
    
    # Compute AND of all three constraints
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]],
            ancilla_qubits[3])
    
    # Apply phase
    qc.z(ancilla_qubits[3])
    
    # Uncompute AND
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]],
            ancilla_qubits[3])
    
    # Uncompute constraints
    uncompute_different_color(problem_qubits[4], problem_qubits[5],
                             problem_qubits[6], problem_qubits[7],
                             ancilla_qubits[2])
    uncompute_different_color(problem_qubits[2], problem_qubits[3],
                             problem_qubits[4], problem_qubits[5],
                             ancilla_qubits[1])
    uncompute_different_color(problem_qubits[0], problem_qubits[1],
                             problem_qubits[2], problem_qubits[3],
                             ancilla_qubits[0])
