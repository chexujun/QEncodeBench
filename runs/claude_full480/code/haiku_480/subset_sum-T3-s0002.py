from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Marks basis states where sum of selected elements equals target 24.
    Elements: a = [6, 5, 12, 6, 6]
    """
    a = [6, 5, 12, 6, 6]
    target = 24  # Binary: 11000
    
    # Use all 6 ancilla qubits as sum register (6 bits handles 0-63)
    s = ancilla_qubits
    
    # === COMPUTE PHASE: Add each element if selected ===
    for idx in range(len(a)):
        _add_controlled(qc, problem_qubits[idx], a[idx], s)
    
    # === APPLY PHASE: Mark states where sum == target ===
    _apply_phase_if_equal(qc, s, target)
    
    # === UNCOMPUTE PHASE: Reverse additions ===
    for idx in range(len(a) - 1, -1, -1):
        _add_controlled(qc, problem_qubits[idx], a[idx], s)


def _add_controlled(qc, ctrl, val, reg):
    """Add classical value val to quantum register reg, controlled by ctrl."""
    if val == 0:
        return
    
    # Ripple-carry addition using only standard gates
    # Carry is tracked through controlled operations
    carry = ctrl
    
    for i in range(len(reg)):
        val_bit = (val >> i) & 1
        
        if val_bit == 1:
            # Compute: new_reg[i] = reg[i] XOR carry
            qc.cx(carry, reg[i])
            
            # Propagate carry for next position
            # carry_next = carry AND original_reg[i]
            # Use Toffoli-based approach: create controlled carry update
            if i < len(reg) - 1:
                # Compute carry_next into reg[i] temporarily
                # After CX, reg[i] = original XOR carry
                # We need: new_carry = original AND carry
                # Technique: Use CCX with creative qubit assignment
                # CCX(carry, original_reg[i], target) flips target when both are 1
                # But original_reg[i] is now flipped, so we must compensate
                
                # Standard ripple-carry trick:
                # Use the modified reg[i] to encode next carry via conditional gates
                qc.ccx(carry, reg[i], reg[i + 1])
                # Now propagate for subsequent iterations using conditional adds
                qc.cx(reg[i], carry)
                qc.cx(carry, reg[i])


def _apply_phase_if_equal(qc, reg, target):
    """Apply Z gate (phase -1) if register equals target."""
    # target = 24 = 0b11000 = [0,0,0,1,1,0] in LSB-first
    target_bits = format(target, f'0{len(reg)}b')[::-1]
    
    # Flip qubits that should be 0 in target
    for i in range(len(reg)):
        if target_bits[i] == '0':
            qc.x(reg[i])
    
    # Now: all qubits are 1 iff original matched target
    # Apply multi-controlled phase gate using mcp
    # mcp applies phase to target qubit when all controls are 1
    # Use first 5 qubits as controls, last as target
    qc.mcp(np.pi, reg[:5], reg[5])
    
    # Flip back the bits
    for i in range(len(reg)):
        if target_bits[i] == '0':
            qc.x(reg[i])
