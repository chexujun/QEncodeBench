from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    elements = [13, 10, 5, 14, 3]
    target = 37
    
    sum_reg = ancilla_qubits[:6]
    
    def controlled_add_constant(qc, ctrl, const_val, reg):
        """Add const_val to reg when ctrl is 1, using ripple-carry."""
        
        carries = []
        
        # Forward pass: compute and store carries
        for i in range(6):
            const_bit = (const_val >> i) & 1
            carry_in = carries[i-1] if i > 0 else None
            
            if i < 5:
                carry_out = ancilla_qubits[6 + i]
                carries.append(carry_out)
            else:
                carries.append(None)
            
            if const_bit:
                if carry_in:
                    # Compute carry: reg[i] OR carry_in (when const_bit=1)
                    qc.cx(reg[i], carries[i])
                    qc.cx(carry_in, carries[i])
                    qc.ccx(reg[i], carry_in, carries[i])
                else:
                    # Compute carry: ctrl AND reg[i]
                    qc.ccx(ctrl, reg[i], carries[i])
            else:
                if carry_in:
                    # Compute carry: reg[i] AND carry_in
                    qc.ccx(reg[i], carry_in, carries[i])
        
        # Compute and apply sum bits
        for i in range(6):
            const_bit = (const_val >> i) & 1
            carry_in = carries[i-1] if i > 0 else None
            
            if const_bit:
                qc.cx(ctrl, reg[i])
            if carry_in:
                qc.cx(carry_in, reg[i])
        
        # Backward pass: uncompute carries
        for i in range(5, -1, -1):
            const_bit = (const_val >> i) & 1
            carry_in = carries[i-1] if i > 0 else None
            carry_out = carries[i]
            
            if carry_out is not None:
                if const_bit:
                    if carry_in:
                        qc.ccx(reg[i], carry_in, carry_out)
                        qc.cx(reg[i], carry_out)
                        qc.cx(carry_in, carry_out)
                    else:
                        qc.ccx(ctrl, reg[i], carry_out)
                else:
                    if carry_in:
                        qc.ccx(reg[i], carry_in, carry_out)
    
    # Compute sum of selected elements
    for idx, elem in enumerate(elements):
        controlled_add_constant(qc, problem_qubits[idx], elem, sum_reg)
    
    # Apply phase -1 when sum == 37 (binary: 100101)
    # Flip bits that should be 0
    for bit in [1, 3, 4]:
        qc.x(sum_reg[bit])
    
    # Multi-controlled phase gate (apply pi phase when all bits are 1)
    qc.mcp(pi, sum_reg[:-1], sum_reg[-1])
    
    # Flip bits back
    for bit in [1, 3, 4]:
        qc.x(sum_reg[bit])
    
    # Uncompute: reverse the sum computation
    for idx in range(len(elements) - 1, -1, -1):
        controlled_add_constant(qc, problem_qubits[idx], elements[idx], sum_reg)
