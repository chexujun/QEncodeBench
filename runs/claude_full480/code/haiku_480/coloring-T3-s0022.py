from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    edges = [(0, 2), (0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]
    
    # Ancilla allocation
    main = ancilla_qubits[0]  # Accumulates AND of all edge checks
    qc.x(main)  # Initialize to |1>
    
    temp = ancilla_qubits[1]  # Temporary for edge validity
    work1 = ancilla_qubits[2]  # Work qubit
    work2 = ancilla_qubits[3]  # Work qubit
    
    def compute_same_color(u, v):
        """Compute (colors same) into temp; returns temp"""
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Condition 1: (b0_u == b0_v) AND (b1_u == b1_v)
        qc.cx(b0_u, work1)
        qc.cx(b0_v, work1)
        qc.x(work1)  # work1 = NOT(b0_u XOR b0_v)
        
        qc.cx(b1_u, work2)
        qc.cx(b1_v, work2)
        qc.x(work2)  # work2 = NOT(b1_u XOR b1_v)
        
        qc.ccx(work1, work2, temp)  # temp = cond 1
        
        # Uncompute work qubits
        qc.x(work2)
        qc.cx(b1_v, work2)
        qc.cx(b1_u, work2)
        
        qc.x(work1)
        qc.cx(b0_v, work1)
        qc.cx(b0_u, work1)
        
        # Condition 2: (b0_u==1 AND b1_u==0) AND (b0_v==1 AND b1_v==0)
        qc.cx(b0_u, work1)
        qc.x(work1)  # work1 = NOT b0_u... actually build differently
        
        # More efficient: use available qubits to build condition 2
        qc.cx(b1_u, work1)  # work1 = b1_u
        qc.x(work1)  # work1 = NOT b1_u
        
        qc.cx(b0_u, work2)
        # work2 = b0_u; now AND: work2 &= work1 (i.e., b0_u AND NOT b1_u)
        qc.ccx(work1, work2, work1)  # work1 = work1 AND work2 (clobbering)
        # Need auxiliary for this; use temp as intermediate
        
        # Cleaner approach: compute each condition separately and OR them
        # Condition 2: b0_u AND NOT b1_u AND b0_v AND NOT b1_v
        qc.x(b1_u)
        qc.ccx(b0_u, b1_u, work1)
        qc.x(b1_u)  # work1 = b0_u AND NOT b1_u
        
        qc.x(b1_v)
        qc.ccx(b0_v, b1_v, work2)
        qc.x(b1_v)  # work2 = b0_v AND NOT b1_v
        
        qc.ccx(work1, work2, work1)  # work1 = cond 2 (reuse work1)
        # OR into temp (use X to negate, CCX to compute, X to un-negate for OR)
        qc.x(temp)
        qc.x(work1)
        qc.ccx(temp, work1, work1)
        qc.x(work1)
        qc.x(temp)  # temp |= work1 (in a sense)
        
        # This is getting complex; simplify by computing all conditions into temp with OR logic
        # After cond 1: temp has it
        # For cond 2: if true, set temp = 1 (temp |= cond2)
        # qc.cx(cond2, temp) when cond2=1 flips temp; not direct OR
        
        # Use: temp = temp OR work1 via: if NOT temp AND work1, flip temp
        # Equivalently: if temp == 0 and work1 == 1, flip temp
        qc.x(temp)
        qc.ccx(temp, work1, temp)  # Now temp might have changed
        qc.x(temp)
        
        # Uncompute work qubits for condition 2
        qc.x(b1_v)
        qc.ccx(b0_v, b1_v, work2)
        qc.x(b1_v)
        
        qc.x(b1_u)
        qc.ccx(b0_u, b1_u, work1)
        qc.x(b1_u)
        
        # Condition 3: NOT b0_u AND b1_u AND NOT b0_v AND b1_v
        qc.x(b0_u)
        qc.ccx(b0_u, b1_u, work1)
        qc.x(b0_u)  # work1 = NOT b0_u AND b1_u
        
        qc.x(b0_v)
        qc.ccx(b0_v, b1_v, work2)
        qc.x(b0_v)  # work2 = NOT b0_v AND b1_v
        
        qc.ccx(work1, work2, work1)  # work1 = cond 3
        
        # OR into temp: temp |= work1
        qc.x(temp)
        qc.ccx(temp, work1, temp)
        qc.x(temp)
        
        # Uncompute
        qc.x(b0_v)
        qc.ccx(b0_v, b1_v, work2)
        qc.x(b0_v)
        
        qc.x(b0_u)
        qc.ccx(b0_u, b1_u, work1)
        qc.x(b0_u)
    
    # Forward pass
    for u, v in edges:
        compute_same_color(u, v)
        qc.x(temp)  # temp = colors_differ
        
        # Update main: main &= temp
        qc.ccx(main, temp, work1)
        qc.swap(main, work1)
        qc.ccx(main, temp, work1)
        
        qc.x(temp)  # Reset temp
    
    # Apply phase
    qc.z(main)
    
    # Backward pass (uncompute)
    for u, v in reversed(edges):
        compute_same_color(u, v)
        qc.x(temp)
        qc.ccx(main, temp, work1)
        qc.swap(main, work1)
        qc.ccx(main, temp, work1)
        qc.x(temp)
    
    # Reset main
    qc.x(main)
