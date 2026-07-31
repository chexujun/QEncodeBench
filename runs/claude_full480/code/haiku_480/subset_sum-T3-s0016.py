from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    """
    Subset sum oracle for Grover's algorithm.
    Marks states where selected elements sum to 26.
    Elements: [9, 12, 2, 9, 15]
    """
    a = [9, 12, 2, 9, 15]
    target = 26
    n_sum = 6
    
    sum_qubits = ancilla_qubits[:n_sum]
    
    # COMPUTE: Add each selected element to sum register
    for i in range(len(a)):
        controlled_add(qc, problem_qubits[i], sum_qubits, a[i])
    
    # PHASE: Apply Z gate if sum equals target
    mark_if_equal(qc, sum_qubits, target)
    
    # UNCOMPUTE: Reverse all additions by subtracting each element
    for i in range(len(a) - 1, -1, -1):
        controlled_sub(qc, problem_qubits[i], sum_qubits, a[i])


def controlled_add(qc: QuantumCircuit, control: int, reg: list, value: int) -> None:
    """Controlled in-place addition of value to register."""
    n = len(reg)
    for i in range(n):
        if (value >> i) & 1:
            qc.cx(control, reg[i])
            for j in range(i + 1, n):
                qc.ccx(reg[j - 1], control, reg[j])


def controlled_sub(qc: QuantumCircuit, control: int, reg: list, value: int) -> None:
    """Controlled in-place subtraction using modular arithmetic."""
    n = len(reg)
    mod_val = (1 << n) - value
    controlled_add(qc, control, reg, mod_val)


def mark_if_equal(qc: QuantumCircuit, reg: list, target: int) -> None:
    """Apply Z phase to all qubits when register equals target."""
    n = len(reg)
    target_bits = [(target >> i) & 1 for i in range(n)]
    
    # Flip bits where target has 0 (to make all target bits = 1)
    for i in range(n):
        if target_bits[i] == 0:
            qc.x(reg[i])
    
    # Apply multi-controlled Z phase
    if n == 1:
        qc.z(reg[0])
    elif n == 2:
        qc.cz(reg[0], reg[1])
    else:
        qc.mcp(math.pi, reg[:-1], reg[-1])
    
    # Flip bits back
    for i in range(n):
        if target_bits[i] == 0:
            qc.x(reg[i])
