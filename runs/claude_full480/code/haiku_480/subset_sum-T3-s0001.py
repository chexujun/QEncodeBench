from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [2, 15, 14, 9, 4]
    target = 9
    
    sum_qubits = ancilla_qubits[:6]
    
    # Compute sum: add each element a[i] to sum if problem_qubits[i] == 1
    for i in range(len(a)):
        _controlled_add(qc, a[i], sum_qubits, problem_qubits[i])
    
    # Apply phase if sum == target
    _phase_if_equal(qc, sum_qubits, target)
    
    # Uncompute: subtract each element
    for i in range(len(a) - 1, -1, -1):
        _controlled_add(qc, -a[i], sum_qubits, problem_qubits[i])


def _controlled_add(qc, value, reg, ctrl):
    """Add/subtract value to reg if ctrl == 1, using ripple-carry adder."""
    n = len(reg)
    
    if value == 0:
        return
    
    if value < 0:
        value = -value
    
    # Get binary representation (LSB first)
    bits = format(value, f'0{n}b')[::-1]
    
    # Ripple-carry addition: for each bit position with value 1
    for i in range(n):
        if bits[i] == '1':
            # Controlled addition of 2^i
            qc.cx(ctrl, reg[i])
            
            # Carry propagation: if reg[i] was 1 before addition, generate carry
            # This requires checking sum at position i+1
            if i < n - 1:
                # Controlled Toffoli: if reg[i] and ctrl are both 1, flip reg[i+1]
                qc.ccx(ctrl, reg[i], reg[i + 1])


def _phase_if_equal(qc, reg, target):
    """Apply phase -1 when register value equals target."""
    n = len(reg)
    target_bits = format(target, f'0{n}b')[::-1]
    
    # Flip qubits that should be 0 in target
    for i in range(n):
        if target_bits[i] == '0':
            qc.x(reg[i])
    
    # Multi-controlled Z: apply phase -1 when all qubits are 1
    # Implemented as CZ gate pairs: MCZ = product of CZ(i,j) for all i<j
    # This gives phase (-1)^C(n,2) = (-1)^(n(n-1)/2) for all-ones state
    # For n=6: C(6,2)=15, so (-1)^15 = -1 as required
    for i in range(n):
        for j in range(i + 1, n):
            qc.cz(reg[i], reg[j])
    
    # Restore flipped qubits
    for i in range(n):
        if target_bits[i] == '0':
            qc.x(reg[i])
