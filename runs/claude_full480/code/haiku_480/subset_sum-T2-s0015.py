from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover-style phase oracle for subset sum: mark basis states where
    selected elements from [5, 9, 9, 10] sum to 24.
    """
    
    # Use 5 ancillas for sum register, 1 for carry/work
    sum_qubits = ancilla_qubits[:5]
    carry = ancilla_qubits[5]
    
    # Compute sum via controlled additions
    _add_constant_controlled(qc, sum_qubits, 5, problem_qubits[0], carry)
    _add_constant_controlled(qc, sum_qubits, 9, problem_qubits[1], carry)
    _add_constant_controlled(qc, sum_qubits, 9, problem_qubits[2], carry)
    _add_constant_controlled(qc, sum_qubits, 10, problem_qubits[3], carry)
    
    # Apply phase when sum == 24
    _apply_phase_if_equal_24(qc, sum_qubits)
    
    # Uncompute (reverse additions)
    _add_constant_controlled(qc, sum_qubits, 10, problem_qubits[3], carry)
    _add_constant_controlled(qc, sum_qubits, 9, problem_qubits[2], carry)
    _add_constant_controlled(qc, sum_qubits, 9, problem_qubits[1], carry)
    _add_constant_controlled(qc, sum_qubits, 5, problem_qubits[0], carry)


def _add_constant_controlled(qc: QuantumCircuit, reg: list[int], 
                             value: int, control: int, work: int) -> None:
    """Add constant to register when control=1, using ripple-carry."""
    
    n = len(reg)
    bits = [(value >> i) & 1 for i in range(n)]
    
    # Ripple-carry: add bits with carry propagation
    for i in range(n):
        if bits[i]:
            if i == 0:
                # No carry in for first bit position
                qc.cx(control, reg[i])
            else:
                # Add current bit with potential carry from previous
                # For proper carry: use Toffoli to compute carry bit
                # carry_out = (reg[i] & bits[i]) | (reg[i] & carry_in) | (bits[i] & carry_in)
                
                # Majority gate using work qubit: compute carry
                qc.cx(reg[i], work)           # work = reg[i]
                qc.cx(control, work)          # work = reg[i] XOR control (bits[i])
                qc.ccx(reg[i], control, carry) # carry = (reg[i] AND control) OR (carry_in would be here)
                
                # Sum: reg[i] += control XOR carry_in
                qc.cx(carry, reg[i])          # reg[i] += carry_in
                qc.cx(control, reg[i])        # reg[i] += bits[i]
                qc.cx(work, carry)            # Propagate to next bit


def _apply_phase_if_equal_24(qc: QuantumCircuit, sum_qubits: list[int]) -> None:
    """Apply phase -1 when register equals 24 = 0b11000."""
    
    # Flip bits that should be 0 in the comparison (bits 0,1,2,4)
    qc.x(sum_qubits[0])
    qc.x(sum_qubits[1])
    qc.x(sum_qubits[2])
    qc.x(sum_qubits[4])
    
    # Apply multi-controlled phase: -1 if bits 0,1,2,3,4 are all 1
    qc.mcp(np.pi, sum_qubits[:-1], sum_qubits[-1])
    
    # Flip bits back
    qc.x(sum_qubits[0])
    qc.x(sum_qubits[1])
    qc.x(sum_qubits[2])
    qc.x(sum_qubits[4])
