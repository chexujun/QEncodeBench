from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    elements = [11, 6, 5, 11, 6]
    target = 22
    
    # Use all 6 ancilla qubits as the sum register (6 bits can represent 0-63)
    sum_reg = ancilla_qubits
    
    # Compute phase: add each element to sum register, controlled by problem qubits
    for i, elem in enumerate(elements):
        add_controlled(qc, sum_reg, problem_qubits[i], elem)
    
    # Apply phase if sum equals target
    apply_phase_if_equal(qc, sum_reg, target)
    
    # Uncompute: subtract each element in reverse order
    for i in range(len(elements) - 1, -1, -1):
        subtract_controlled(qc, sum_reg, problem_qubits[i], elements[i])


def add_controlled(qc, reg, control, value):
    """Add value to reg if control==1, using ripple-carry adder"""
    bits = format(value, f'0{len(reg)}b')[::-1]
    carry = control
    
    for i in range(len(reg) - 1):
        if bits[i] == '1':
            # Compute carry_out = old_reg[i] AND carry, store in reg[i+1]
            qc.ccx(reg[i], carry, reg[i+1])
            # Update sum bit: reg[i] XOR= control XOR carry
            qc.cx(control, reg[i])
            qc.cx(carry, reg[i])
        else:
            # Carry propagation when bit is 0
            qc.ccx(reg[i], carry, reg[i+1])
            qc.cx(carry, reg[i])
        
        carry = reg[i+1]
    
    # Handle MSB
    if bits[-1] == '1':
        qc.cx(control, reg[-1])
        qc.cx(carry, reg[-1])
    else:
        qc.cx(carry, reg[-1])


def subtract_controlled(qc, reg, control, value):
    """Subtract value from reg if control==1 (reverse of add_controlled)"""
    bits = format(value, f'0{len(reg)}b')[::-1]
    
    # MSB first (reverse order)
    if bits[-1] == '1':
        carry = reg[-1]
        qc.cx(carry, reg[-1])
        qc.cx(control, reg[-1])
    else:
        carry = reg[-1]
        qc.cx(carry, reg[-1])
    
    for i in range(len(reg) - 2, -1, -1):
        reg_next = reg[i + 1]
        if bits[i] == '1':
            qc.cx(carry, reg[i])
            qc.cx(control, reg[i])
            qc.ccx(reg[i], carry, reg_next)
        else:
            qc.cx(carry, reg[i])
            qc.ccx(reg[i], carry, reg_next)
        carry = reg_next


def apply_phase_if_equal(qc, reg, target):
    """Apply Z phase if reg == target (22 = 0b010110)"""
    target_bits = format(target, f'0{len(reg)}b')[::-1]
    
    # Flip bits where target is 0, so all bits are 1 iff reg==target
    for i, bit in enumerate(target_bits):
        if bit == '0':
            qc.x(reg[i])
    
    # Apply multi-controlled Z using nested controlled phase gates
    # Build up the controlled phase by passing through each qubit
    for i in range(len(reg) - 1):
        qc.cp(3.141592653589793 / (1 << (len(reg) - i - 1)), reg[i], reg[i + 1])
    
    # Flip back
    for i, bit in enumerate(target_bits):
        if bit == '0':
            qc.x(reg[i])
