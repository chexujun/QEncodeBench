from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute NOT(x[i] OR x[j]) for each edge constraint
    # Using formula: NOT(a OR b) = 1 - a - b + ab
    # Implemented as: c = 1; c ^= a; c ^= b; c ^= (a AND b)
    
    # a[0] = NOT(x[0] OR x[1])
    qc.x(a[0])
    qc.cx(x[0], a[0])
    qc.cx(x[1], a[0])
    qc.ccx(x[0], x[1], a[0])
    
    # a[1] = NOT(x[0] OR x[2])
    qc.x(a[1])
    qc.cx(x[0], a[1])
    qc.cx(x[2], a[1])
    qc.ccx(x[0], x[2], a[1])
    
    # a[2] = NOT(x[2] OR x[3])
    qc.x(a[2])
    qc.cx(x[2], a[2])
    qc.cx(x[3], a[2])
    qc.ccx(x[2], x[3], a[2])
    
    # Compute size constraint: accumulate "at least 3 bits set" into a[3]
    # Check all C(4,3) combinations of three qubits
    
    qc.ccx(x[0], x[1], a[4])
    qc.ccx(a[4], x[2], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[2], a[5])
    qc.ccx(x[0], x[1], a[4])
    
    qc.ccx(x[0], x[1], a[4])
    qc.ccx(a[4], x[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[3], a[5])
    qc.ccx(x[0], x[1], a[4])
    
    qc.ccx(x[0], x[2], a[4])
    qc.ccx(a[4], x[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[3], a[5])
    qc.ccx(x[0], x[2], a[4])
    
    qc.ccx(x[1], x[2], a[4])
    qc.ccx(a[4], x[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[3], a[5])
    qc.ccx(x[1], x[2], a[4])
    
    # Check if all constraints are satisfied (all of a[0..3] == 0)
    # a[4] = 1 iff state is valid
    qc.x(a[4])
    qc.cx(a[0], a[4])
    qc.cx(a[1], a[4])
    qc.cx(a[2], a[4])
    qc.cx(a[3], a[4])
    
    # Apply phase -1 to valid states
    qc.z(a[4])
    
    # Uncompute a[4]
    qc.cx(a[3], a[4])
    qc.cx(a[2], a[4])
    qc.cx(a[1], a[4])
    qc.cx(a[0], a[4])
    qc.x(a[4])
    
    # Uncompute size constraint (reverse order)
    qc.ccx(x[1], x[2], a[4])
    qc.ccx(a[4], x[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[3], a[5])
    qc.ccx(x[1], x[2], a[4])
    
    qc.ccx(x[0], x[2], a[4])
    qc.ccx(a[4], x[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[3], a[5])
    qc.ccx(x[0], x[2], a[4])
    
    qc.ccx(x[0], x[1], a[4])
    qc.ccx(a[4], x[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[3], a[5])
    qc.ccx(x[0], x[1], a[4])
    
    qc.ccx(x[0], x[1], a[4])
    qc.ccx(a[4], x[2], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(a[4], x[2], a[5])
    qc.ccx(x[0], x[1], a[4])
    
    # Uncompute edge constraints (reverse order)
    qc.ccx(x[2], x[3], a[2])
    qc.cx(x[3], a[2])
    qc.cx(x[2], a[2])
    qc.x(a[2])
    
    qc.ccx(x[0], x[2], a[1])
    qc.cx(x[2], a[1])
    qc.cx(x[0], a[1])
    qc.x(a[1])
    
    qc.ccx(x[0], x[1], a[0])
    qc.cx(x[1], a[0])
    qc.cx(x[0], a[0])
    qc.x(a[0])
