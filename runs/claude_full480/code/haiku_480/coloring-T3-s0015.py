from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,4), (1,2), (1,3), (1,4), (2,3), (2,4)]
    
    all_ok = ancilla_qubits[0]
    bit0_xnor = ancilla_qubits[1]
    bit1_xnor = ancilla_qubits[2]
    mono = ancilla_qubits[3]
    
    # COMPUTE: Initialize all_ok to 1
    qc.x(all_ok)
    
    for v1, v2 in edges:
        b0_1 = problem_qubits[2*v1]
        b1_1 = problem_qubits[2*v1 + 1]
        b0_2 = problem_qubits[2*v2]
        b1_2 = problem_qubits[2*v2 + 1]
        
        # Compute bit0_xnor = b0_1 XNOR b0_2
        qc.cx(b0_1, bit0_xnor)
        qc.cx(b0_2, bit0_xnor)
        qc.x(bit0_xnor)
        
        # Compute bit1_xnor = b1_1 XNOR b1_2
        qc.cx(b1_1, bit1_xnor)
        qc.cx(b1_2, bit1_xnor)
        qc.x(bit1_xnor)
        
        # Compute mono = bit0_xnor AND bit1_xnor
        # (true iff colors of v1 and v2 are the same)
        qc.mcx([bit0_xnor, bit1_xnor], mono)
        
        # If this edge is monochromatic, unset all_ok
        qc.cx(mono, all_ok)
    
    # PHASE: Apply Z gate (phase -1 iff all_ok = 1)
    qc.z(all_ok)
    
    # UNCOMPUTE: Reverse all steps
    for v1, v2 in reversed(edges):
        b0_1 = problem_qubits[2*v1]
        b1_1 = problem_qubits[2*v1 + 1]
        b0_2 = problem_qubits[2*v2]
        b1_2 = problem_qubits[2*v2 + 1]
        
        qc.cx(mono, all_ok)
        qc.mcx([bit0_xnor, bit1_xnor], mono)
        
        qc.x(bit1_xnor)
        qc.cx(b1_2, bit1_xnor)
        qc.cx(b1_1, bit1_xnor)
        
        qc.x(bit0_xnor)
        qc.cx(b0_2, bit0_xnor)
        qc.cx(b0_1, bit0_xnor)
    
    qc.x(all_ok)
