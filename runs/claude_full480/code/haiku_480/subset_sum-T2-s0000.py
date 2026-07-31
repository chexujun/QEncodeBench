from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Phase oracle for subset sum problem: apply -1 phase when selected elements sum to 12.
    Elements: a = [2, 7, 1, 4]
    """
    a = ancilla_qubits
    p = problem_qubits
    values = [2, 7, 1, 4]
    
    def add_constant_controlled(ctrl_qubit, const_value):
        """Controlled ripple-carry addition: ancilla += const_value when ctrl_qubit == 1."""
        for bit_idx in range(4):
            if (const_value >> bit_idx) & 1:
                if bit_idx < 3:
                    qc.ccx(ctrl_qubit, a[bit_idx], a[bit_idx + 1])
                qc.cx(ctrl_qubit, a[bit_idx])
    
    def add_constant_controlled_inverse(ctrl_qubit, const_value):
        """Inverse of controlled addition (for uncomputation)."""
        for bit_idx in range(3, -1, -1):
            if (const_value >> bit_idx) & 1:
                qc.cx(ctrl_qubit, a[bit_idx])
                if bit_idx < 3:
                    qc.ccx(ctrl_qubit, a[bit_idx], a[bit_idx + 1])
    
    # Compute phase: add 2*p[0] + 7*p[1] + 1*p[2] + 4*p[3] into ancillas
    for i in range(4):
        add_constant_controlled(p[i], values[i])
    
    # Phase application: apply -1 if sum == 12 (binary 1100)
    # Flip a[0] and a[1] so that state 1100 becomes 1111
    qc.x(a[0])
    qc.x(a[1])
    
    # Apply multi-controlled phase gate: -1 when a[0]=a[1]=a[2]=a[3]=1
    qc.mcp(np.pi, a[:3], a[3])
    
    # Restore a[0] and a[1] to their previous state
    qc.x(a[0])
    qc.x(a[1])
    
    # Uncompute phase: remove all added values (in reverse order)
    for i in range(3, -1, -1):
        add_constant_controlled_inverse(p[i], values[i])
