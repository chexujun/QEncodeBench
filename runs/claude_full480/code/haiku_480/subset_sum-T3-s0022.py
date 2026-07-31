from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for subset sum: mark states where selected elements sum to 4.
    With a = [15, 10, 9, 4, 13], only x = [0,0,0,1,0] (selecting a[3]=4) satisfies the constraint.
    
    Strategy: flip problem qubits so target state becomes all |1>, use Toffoli chain
    to compute AND of all qubits, apply phase, then uncompute.
    """
    p = problem_qubits
    a = ancilla_qubits
    
    # Flip qubits to convert target state |00100> to |11111>
    qc.x(p[0])
    qc.x(p[1])
    qc.x(p[2])
    # p[3] is already 1
    qc.x(p[4])
    
    # Compute AND of all problem qubits via Toffoli chain
    qc.cx(p[0], a[0])           # a[0] = p[0]
    qc.ccx(a[0], p[1], a[1])    # a[1] = a[0] AND p[1]
    qc.ccx(a[1], p[2], a[2])    # a[2] = a[1] AND p[2]
    qc.ccx(a[2], p[3], a[3])    # a[3] = a[2] AND p[3]
    qc.ccx(a[3], p[4], a[4])    # a[4] = a[3] AND p[4]
    
    # Apply phase -1 to solution state (when all problem qubits are |1>)
    qc.z(a[4])
    
    # Uncompute: reverse Toffoli chain
    qc.ccx(a[3], p[4], a[4])
    qc.ccx(a[2], p[3], a[3])
    qc.ccx(a[1], p[2], a[2])
    qc.ccx(a[0], p[1], a[1])
    qc.cx(p[0], a[0])
    
    # Unflip the X gates
    qc.x(p[4])
    qc.x(p[2])
    qc.x(p[1])
    qc.x(p[0])
