from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for each free cell
    # Cell 0 (row 0, col 0): free_cell_0 encodes to 2 -> must be 10
    a0, a1 = problem_qubits[0], problem_qubits[1]
    # Cell 1 (row 0, col 1): free_cell_1 encodes to 1 -> must be 01
    b0, b1 = problem_qubits[2], problem_qubits[3]
    # Cell 2 (row 0, col 2): free_cell_2 encodes to 0 -> must be 00 or 11
    c0, c1 = problem_qubits[4], problem_qubits[5]
    # Cell 3 (row 2, col 0): free_cell_3 encodes to 0 -> must be 00 or 11
    d0, d1 = problem_qubits[6], problem_qubits[7]
    
    # Ancilla allocation
    e0 = ancilla_qubits[0]     # Check cell 0 = 10
    e1 = ancilla_qubits[1]     # Check cell 1 = 01
    e2 = ancilla_qubits[2]     # Check cell 2 = 0
    e3 = ancilla_qubits[3]     # Check cell 3 = 0
    temp = ancilla_qubits[4]   # Temporary for XOR computations
    e_all = ancilla_qubits[5]  # Combined AND of all checks
    
    # Compute e0: detect if cell 0 is encoded as 10 (a0=0, a1=1)
    # Condition: NOT a0 AND a1
    qc.x(a0)
    qc.ccx(a0, a1, e0)
    qc.x(a0)
    
    # Compute e1: detect if cell 1 is encoded as 01 (b0=1, b1=0)
    # Condition: b0 AND NOT b1
    qc.x(b1)
    qc.ccx(b0, b1, e1)
    qc.x(b1)
    
    # Compute e2: detect if cell 2 encodes to 0 (c0 XNOR c1)
    # Codes 00 and 11 both map to 0; c0 XNOR c1 = NOT(c0 XOR c1)
    qc.cx(c0, temp)      # temp = c0
    qc.cx(c1, temp)      # temp = c0 XOR c1
    qc.x(temp)           # temp = NOT(c0 XOR c1)
    qc.cx(temp, e2)      # e2 = NOT(c0 XOR c1)
    qc.x(temp)           # temp = c0 XOR c1 (restore for uncompute)
    qc.cx(c1, temp)      # temp = c0
    qc.cx(c0, temp)      # temp = 0 (uncompute complete)
    
    # Compute e3: detect if cell 3 encodes to 0 (d0 XNOR d1)
    qc.cx(d0, temp)      # temp = d0
    qc.cx(d1, temp)      # temp = d0 XOR d1
    qc.x(temp)           # temp = NOT(d0 XOR d1)
    qc.cx(temp, e3)      # e3 = NOT(d0 XOR d1)
    qc.x(temp)           # temp = d0 XOR d1
    qc.cx(d1, temp)      # temp = d0
    qc.cx(d0, temp)      # temp = 0
    
    # Compute e_all = e0 AND e1 AND e2 AND e3 using multi-controlled X
    qc.mcx([e0, e1, e2, e3], e_all)
    
    # Apply phase: Z gate flips sign when e_all == 1
    qc.z(e_all)
    
    # Uncompute e_all
    qc.mcx([e0, e1, e2, e3], e_all)
    
    # Uncompute e3
    qc.cx(d0, temp)
    qc.cx(d1, temp)
    qc.x(temp)
    qc.cx(temp, e3)
    qc.x(temp)
    qc.cx(d1, temp)
    qc.cx(d0, temp)
    
    # Uncompute e2
    qc.cx(c0, temp)
    qc.cx(c1, temp)
    qc.x(temp)
    qc.cx(temp, e2)
    qc.x(temp)
    qc.cx(c1, temp)
    qc.cx(c0, temp)
    
    # Uncompute e1
    qc.x(b1)
    qc.ccx(b0, b1, e1)
    qc.x(b1)
    
    # Uncompute e0
    qc.x(a0)
    qc.ccx(a0, a1, e0)
    qc.x(a0)
