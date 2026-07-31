from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Phase oracle for subset sum: mark states where selected elements sum to 40.
    problem_qubits[i] indicates whether element a[i] is selected.
    Uses ancilla_qubits as a binary register to accumulate the sum.
    """
    a = [15, 11, 9, 13, 7]
    target = 40
    
    sum_reg = ancilla_qubits
    
    # Compute phase: add each selected element to the sum register
    for i in range(len(a)):
        _controlled_add(qc, problem_qubits[i], a[i], sum_reg)
    
    # Apply phase: -1 if sum equals target
    _phase_if_equal(qc, sum_reg, target)
    
    # Uncompute: subtract to restore ancillas to |0⟩
    for i in range(len(a) - 1, -1, -1):
        _controlled_subtract(qc, problem_qubits[i], a[i], sum_reg)

def _controlled_add(qc: QuantumCircuit, control: int, value: int, 
                    reg: list[int]) -> None:
    """
    Add value to reg when control is 1, using ripple-carry with Toffoli gates.
    """
    n = len(reg)
    bits = format(value, f'0{n}b')
    
    for i in range(n):
        if bits[n - 1 - i] == '1':
            qc.cx(control, reg[i])
            # Propagate carry: if bit i is now 1, propagate to higher bits
            for j in range(i + 1, n):
                qc.ccx(control, reg[i], reg[j])

def _controlled_subtract(qc: QuantumCircuit, control: int, value: int,
                         reg: list[int]) -> None:
    """
    Subtract value from reg when control is 1 (reverse of controlled_add).
    Process bits in reverse order for proper uncomputation.
    """
    n = len(reg)
    bits = format(value, f'0{n}b')
    
    for i in range(n - 1, -1, -1):
        if bits[n - 1 - i] == '1':
            # Reverse carry propagation
            for j in range(i + 1, n):
                qc.ccx(control, reg[i], reg[j])
            qc.cx(control, reg[i])

def _phase_if_equal(qc: QuantumCircuit, sum_reg: list[int], 
                    target: int) -> None:
    """
    Apply Z gate (phase -1) when sum_reg equals target in binary.
    Uses multi-controlled Z: decomposed as H-MCX-H on target qubit.
    """
    n = len(sum_reg)
    target_bits = format(target, f'0{n}b')
    
    # Flip qubits that should be 0 in the target
    for i in range(n):
        if target_bits[n - 1 - i] == '0':
            qc.x(sum_reg[i])
    
    # Multi-controlled Z via H-MCX-H decomposition
    qc.h(sum_reg[n - 1])
    qc.mcx(sum_reg[:-1], sum_reg[n - 1])
    qc.h(sum_reg[n - 1])
    
    # Flip bits back
    for i in range(n):
        if target_bits[n - 1 - i] == '0':
            qc.x(sum_reg[i])
