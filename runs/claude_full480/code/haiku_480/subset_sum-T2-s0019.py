from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0], x[1], x[2], x[3]
    a = ancilla_qubits  # a[0], a[1], a[2], a[3]
    
    # Oracle for: sum == 1, where sum = 3*x[0] + 1*x[1] + 1*x[2] + 7*x[3]
    # This is true iff: (NOT x[0]) AND (x[1] XOR x[2]) AND (NOT x[3])
    # because the only ways to sum to 1 are:
    # - x[0]=0, x[1]=1, x[2]=0, x[3]=0 (select a[1]=1)
    # - x[0]=0, x[1]=0, x[2]=1, x[3]=0 (select a[2]=1)
    
    # COMPUTE PHASE: compute condition into ancillas
    
    # Step 1: Compute x[1] XOR x[2] into a[0]
    qc.cx(x[1], a[0])
    qc.cx(x[2], a[0])
    
    # Step 2: Compute (NOT x[0]) AND (x[1] XOR x[2]) into a[1]
    # Use X gates around control to flip the logic
    qc.x(x[0])
    qc.ccx(x[0], a[0], a[1])
    qc.x(x[0])
    
    # Step 3: Compute ((NOT x[0]) AND (x[1] XOR x[2])) AND (NOT x[3]) into a[2]
    qc.x(x[3])
    qc.ccx(x[3], a[1], a[2])
    qc.x(x[3])
    
    # PHASE: Apply Z gate to mark solutions
    qc.z(a[2])
    
    # UNCOMPUTE: Reverse all operations to restore ancillas to |0>
    
    # Reverse Step 3
    qc.x(x[3])
    qc.ccx(x[3], a[1], a[2])
    qc.x(x[3])
    
    # Reverse Step 2
    qc.x(x[0])
    qc.ccx(x[0], a[0], a[1])
    qc.x(x[0])
    
    # Reverse Step 1
    qc.cx(x[2], a[0])
    qc.cx(x[1], a[0])
