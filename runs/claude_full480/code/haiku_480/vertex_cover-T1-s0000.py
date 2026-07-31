def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Identify valid vertex covers of size at most 2 for the graph with edges:
    # (0,1), (0,2), (0,3), (1,3), (2,3)
    # 
    # Checking all size-2 subsets:
    # {0,1}: covers (0,1), (0,2), (0,3), (1,3) - missing (2,3) ✗
    # {0,2}: covers (0,1), (0,2), (0,3), (2,3) - missing (1,3) ✗
    # {0,3}: covers (0,1), (0,2), (0,3), (1,3), (2,3) - all edges! ✓
    # {1,2}: covers (0,1), (0,2), (1,3), (2,3) - missing (0,3) ✗
    # {1,3}: covers (0,1), (0,3), (1,3), (2,3) - missing (0,2) ✗
    # {2,3}: covers (0,2), (0,3), (1,3), (2,3) - missing (0,1) ✗
    # Size-1 subsets don't cover all edges.
    #
    # Only {0,3} is valid: x[0]=1, x[1]=0, x[2]=0, x[3]=1
    
    a = ancilla_qubits[0]
    
    # Compute-phase-uncompute pattern:
    # Compute: x[0] AND NOT x[1] AND NOT x[2] AND x[3] into ancilla
    qc.x(problem_qubits[1])  # Flip to convert to check NOT x[1]
    qc.x(problem_qubits[2])  # Flip to convert to check NOT x[2]
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a)
    qc.x(problem_qubits[2])  # Flip back
    qc.x(problem_qubits[1])  # Flip back
    # Now a=1 iff x[0]=1, x[1]=0, x[2]=0, x[3]=1
    
    # Phase: apply -1 phase if predicate holds
    qc.z(a)
    
    # Uncompute: reverse the compute step
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
    # Ancilla returns to |0>; phase of -1 persists on marked state
