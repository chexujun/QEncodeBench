from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [4, 13, 3, 9, 15]
    target = 19
    
    sum_qubits = ancilla_qubits
    
    # Phase 1: Compute sum into sum_qubits
    for i, value in enumerate(a):
        controlled_add(qc, problem_qubits[i], sum_qubits, value)
    
    # Phase 2: Apply phase if sum == target
    apply_phase_if_equal(qc, sum_qubits, target)
    
    # Phase 3: Uncompute sum (reverse order to leave ancillas in |0⟩)
    for i in range(len(a) - 1, -1, -1):
        controlled_add_reverse(qc, problem_qubits[i], sum_qubits, a[i])


def controlled_add(qc: QuantumCircuit, control: int, sum_qubits: list[int], value: int) -> None:
    """Add value to sum_qubits if control qubit is 1, with carry propagation."""
    n = len(sum_qubits)
    value_bits = [(value >> j) & 1 for j in range(n)]
    
    for j in range(n):
        if value_bits[j] == 1:
            # Propagate carries for this bit position before flipping
            for k in range(j + 1, n):
                qc.ccx(control, sum_qubits[j], sum_qubits[k])
            
            # Flip the bit at position j
            qc.cx(control, sum_qubits[j])


def controlled_add_reverse(qc: QuantumCircuit, control: int, sum_qubits: list[int], value: int) -> None:
    """Reverse of controlled_add (for uncomputation)."""
    n = len(sum_qubits)
    value_bits = [(value >> j) & 1 for j in range(n)]
    
    for j in range(n - 1, -1, -1):
        if value_bits[j] == 1:
            # Unflip the bit at position j
            qc.cx(control, sum_qubits[j])
            
            # Undo carry propagation in reverse
            for k in range(n - 1, j, -1):
                qc.ccx(control, sum_qubits[j], sum_qubits[k])


def apply_phase_if_equal(qc: QuantumCircuit, sum_qubits: list[int], target: int) -> None:
    """Apply phase -1 to computational basis state if sum_qubits == target."""
    n = len(sum_qubits)
    target_bits = format(target, f'0{n}b')[::-1]  # LSB first
    
    # Prepare: X gates on positions where target bit is 0
    for i in range(n):
        if target_bits[i] == '0':
            qc.x(sum_qubits[i])
    
    # Multi-controlled phase gate (applies phase π = -1 when all controls are 1)
    if n == 1:
        qc.z(sum_qubits[0])
    else:
        qc.mcp(np.pi, sum_qubits[:-1], sum_qubits[-1])
    
    # Unprepare: reverse X gates
    for i in range(n):
        if target_bits[i] == '0':
            qc.x(sum_qubits[i])
