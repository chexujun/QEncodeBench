import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Determine the unique valid Latin square solution by constraint propagation:
    # Row/Col 2 are fixed: row 2 = [0,1,2], col 2 = [0,1,2]
    # Col 0: has [2,_,0] → cell(1,0) must be 1
    # Col 1: has [_,2,1] → cell(0,1) must be 0
    # Row 0: has [2,0,_] → cell(0,2) must be 1
    # Row 1: has [1,2,_] → cell(1,2) must be 0
    #
    # Free cells in order: (0,1), (0,2), (1,0), (1,2)
    # Unique solution: cell0=0, cell1=1, cell2=1, cell3=0
    #
    # Encoding (value = b0 + 2*b1):
    # cell0 = 0 → code (00) → problem_qubits[0]=0, problem_qubits[1]=0
    # cell1 = 1 → code (01) → problem_qubits[2]=1, problem_qubits[3]=0
    # cell2 = 1 → code (01) → problem_qubits[4]=1, problem_qubits[5]=0
    # cell3 = 0 → code (00) → problem_qubits[6]=0, problem_qubits[7]=0
    
    # Qubits that must be 1 in the marked state: [2, 4]
    # Qubits that must be 0 in the marked state: [0, 1, 3, 5, 6, 7]
    must_be_zero = [problem_qubits[i] for i in [0, 1, 3, 5, 6, 7]]
    
    anc_mark = ancilla_qubits[0]
    anc_helper = ancilla_qubits[1:6]
    
    # COMPUTE: Flip qubits that should be 0 so all problem qubits become 1 in marked state
    for q in must_be_zero:
        qc.x(q)
    
    # COMPUTE: Set anc_mark=1 iff all problem qubits are 1 (i.e., state is marked)
    qc.mcx(problem_qubits, anc_mark, anc_helper, mode='vchain_dirty')
    
    # PHASE: Apply phase -1 when anc_mark=1
    qc.p(math.pi, anc_mark)
    
    # UNCOMPUTE: Reset anc_mark to 0 and helper ancillas to 0
    qc.mcx(problem_qubits, anc_mark, anc_helper, mode='vchain_dirty')
    
    # UNCOMPUTE: Flip back qubits to restore original values
    for q in must_be_zero:
        qc.x(q)
