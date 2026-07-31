from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Subset sum oracle for a=[8,7,11,2,14], target=18.
    Marks states where selected subset sums to exactly 18.
    """
    
    values = [8, 7, 11, 2, 14]
    target = 18
    target_bits = [(target >> i) & 1 for i in range(6)]
    
    sum_qubits = ancilla_qubits
    
    # COMPUTE: Accumulate sum using ripple-carry addition
    for idx, val in enumerate(values):
        ctrl = problem_qubits[idx]
        
        # Add val to sum_qubits if ctrl = 1, using in-place binary addition
        # Process from LSB to MSB, computing sum bits and implicit carries
        for bit_pos in range(6):
            val_bit = (val >> bit_pos) & 1
            
            if val_bit == 0:
                continue
            
            # This bit of val is 1, so we add it with carry propagation
            # For bit_pos, we XOR in the val_bit (controlled by ctrl)
            qc.cx(ctrl, sum_qubits[bit_pos])
            
            # Handle carry to next bits
            # If bit_pos is set after the addition, we may have a carry
            # Compute carry_out using Toffoli: carry if both operands set
            if bit_pos < 5:
                # Carry generation: if sum_qubits[bit_pos] and ctrl both were 1
                # (before the CX), then we have a carry to bit_pos+1
                # Use CCX to compute: sum_qubits[bit_pos+1] += (ctrl AND original_sum[bit_pos])
                qc.ccx(ctrl, sum_qubits[bit_pos], sum_qubits[bit_pos + 1])
    
    # PHASE: Check if sum equals target = 18 = 0b010010
    # Flip bits that should be 0
    for bit_pos in range(6):
        if target_bits[bit_pos] == 0:
            qc.x(sum_qubits[bit_pos])
    
    # Apply multi-controlled phase: Z if all sum_qubits are 1
    qc.mcp(np.pi, sum_qubits[0:5], sum_qubits[5])
    
    # Unflip bits
    for bit_pos in range(6):
        if target_bits[bit_pos] == 0:
            qc.x(sum_qubits[bit_pos])
    
    # UNCOMPUTE: Reverse addition operations (reverse order)
    for idx in range(len(values) - 1, -1, -1):
        ctrl = problem_qubits[idx]
        val = values[idx]
        
        # Reverse the carry additions
        for bit_pos in range(5, -1, -1):
            val_bit = (val >> bit_pos) & 1
            
            if val_bit == 0:
                continue
            
            # Uncompute carry
            if bit_pos < 5:
                qc.ccx(ctrl, sum_qubits[bit_pos], sum_qubits[bit_pos + 1])
            
            # Uncompute XOR
            qc.cx(ctrl, sum_qubits[bit_pos])
