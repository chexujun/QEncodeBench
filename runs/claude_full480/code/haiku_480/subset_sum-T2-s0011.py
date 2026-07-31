from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for subset sum: marks states where sum of selected elements equals 17.
    Elements a = [7, 7, 10, 4].
    Uses ancilla qubits to compute the sum via ripple-carry addition.
    """
    # Use first 5 ancillas as sum register (5 bits can store 0-31)
    s = ancilla_qubits[:5]
    
    # Compute subset sum into s register
    # Add 7 if problem_qubits[0] = 1
    _add_controlled_constant(qc, problem_qubits[0], 7, s)
    # Add 7 if problem_qubits[1] = 1
    _add_controlled_constant(qc, problem_qubits[1], 7, s)
    # Add 10 if problem_qubits[2] = 1
    _add_controlled_constant(qc, problem_qubits[2], 10, s)
    # Add 4 if problem_qubits[3] = 1
    _add_controlled_constant(qc, problem_qubits[3], 4, s)
    
    # Check if sum equals 17 (binary: 10001) and apply phase
    # Flip bits [1,2,3] to convert to all-ones check
    qc.x(s[1])
    qc.x(s[2])
    qc.x(s[3])
    
    # Multi-controlled Z gate: applies -1 phase when all s qubits are 1
    qc.mcz(s)
    
    # Restore bits
    qc.x(s[3])
    qc.x(s[2])
    qc.x(s[1])
    
    # Uncompute sum in reverse order (with negated values)
    _add_controlled_constant(qc, problem_qubits[3], -4, s)
    _add_controlled_constant(qc, problem_qubits[2], -10, s)
    _add_controlled_constant(qc, problem_qubits[1], -7, s)
    _add_controlled_constant(qc, problem_qubits[0], -7, s)


def _add_controlled_constant(qc: QuantumCircuit, control: int, value: int, 
                             reg: list[int]) -> None:
    """
    Adds/subtracts a constant to register when control=1.
    Implements ripple-carry using CNOT and Toffoli gates.
    """
    if value == 0:
        return
    
    # For subtraction, negate and apply in reverse
    if value < 0:
        value = -value
        reverse = True
    else:
        reverse = False
    
    # Extract bits of the value
    n = len(reg)
    bits = [(value >> i) & 1 for i in range(n)]
    
    # Build gate sequence for ripple-carry
    gates = []
    for i in range(n):
        if bits[i] == 1:
            gates.append(('cx', control, reg[i]))
            if i < n - 1:
                gates.append(('ccx', control, reg[i], reg[i+1]))
    
    # Apply gates in reverse if this is a subtraction uncompute
    if reverse:
        gates.reverse()
    
    for gate in gates:
        if gate[0] == 'cx':
            qc.cx(gate[1], gate[2])
        elif gate[0] == 'ccx':
            qc.ccx(gate[1], gate[2], gate[3])
