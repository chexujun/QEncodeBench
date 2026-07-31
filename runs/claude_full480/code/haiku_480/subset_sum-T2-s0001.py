from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    a = [5, 2, 6, 1]
    sum_reg = ancilla_qubits
    
    # Compute sum into ancilla register
    for i in range(4):
        add_controlled(qc, problem_qubits[i], sum_reg, a[i])
    
    # Apply phase -1 when sum == 13 (binary 1101)
    # Flip bit 1 (the 0 bit in 1101) to make all bits match target
    qc.x(sum_reg[1])
    # Apply 4-controlled phase: phase pi when all control qubits are |1>
    qc.mcp(pi, sum_reg[:3], sum_reg[3])
    # Flip bit 1 back
    qc.x(sum_reg[1])
    
    # Uncompute sum (reverse operations, reverse iteration order)
    for i in range(3, -1, -1):
        add_controlled_inv(qc, problem_qubits[i], sum_reg, a[i])


def add_controlled(qc, control, reg, value):
    """Add value to reg when control==1, using ripple-carry adder."""
    for i in range(4):
        if (value >> i) & 1:
            # Compute and propagate carry before modifying reg[i]
            if i < 3:
                qc.ccx(control, reg[i], reg[i+1])
            # Add bit at position i
            qc.cx(control, reg[i])


def add_controlled_inv(qc, control, reg, value):
    """Inverse of add_controlled: uncomputes by reversing gate order and iteration."""
    for i in range(3, -1, -1):
        if (value >> i) & 1:
            # Reverse order: undo CX first, then CCX
            qc.cx(control, reg[i])
            if i < 3:
                qc.ccx(control, reg[i], reg[i+1])
