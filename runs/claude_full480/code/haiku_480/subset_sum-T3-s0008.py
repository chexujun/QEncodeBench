from math import pi
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """Subset sum oracle: apply phase -1 when selected elements sum to 17."""
    
    p = problem_qubits
    a = ancilla_qubits
    
    def add_const_controlled(constant, control, accumulator):
        """In-place quantum addition: accumulator += constant (if control == 1)."""
        # Convert constant to binary (LSB first)
        bits = [(constant >> i) & 1 for i in range(len(accumulator))]
        n = len(accumulator)
        
        # Forward pass: compute carry bits via CCX
        for i in range(n - 1):
            if bits[i]:
                qc.ccx(control, accumulator[i], accumulator[i + 1])
        
        # Backward pass: compute sum bits and reverse carries
        for i in range(n - 1, -1, -1):
            if bits[i]:
                qc.cx(control, accumulator[i])
            if i > 0:
                qc.ccx(control, accumulator[i - 1], accumulator[i])
    
    # Accumulate sum: a[0:6] will hold the binary representation of sum
    add_const_controlled(4, p[0], a)    # Add 4 if p[0] selected
    add_const_controlled(10, p[1], a)   # Add 10 if p[1] selected
    add_const_controlled(10, p[2], a)   # Add 10 if p[2] selected
    add_const_controlled(3, p[3], a)    # Add 3 if p[3] selected
    add_const_controlled(14, p[4], a)   # Add 14 if p[4] selected
    
    # Check if sum == 17 (binary: 010001 = bits [0, 4] are 1)
    # Flip bits that should be 0 to prepare for multi-control phase gate
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[5])
    
    # Apply phase -1 (via mcp with angle pi) when all ancillas are 1
    qc.mcp(pi, [a[0], a[1], a[2], a[3], a[4], a[5]], a[0])
    
    # Unflip the temporarily flipped bits
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[5])
    
    # Uncompute: reverse the additions in reverse order
    add_const_controlled(14, p[4], a)
    add_const_controlled(3, p[3], a)
    add_const_controlled(10, p[2], a)
    add_const_controlled(10, p[1], a)
    add_const_controlled(4, p[0], a)
