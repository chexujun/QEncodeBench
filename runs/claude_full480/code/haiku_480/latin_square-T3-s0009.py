from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # === COMPUTE ALL CONSTRAINTS ===
    
    # Constraint 0: cell_0 (bits p[0], p[1]) must decode to value 0
    # Value is 0 iff b0 = b1, i.e., NOT(b0 XOR b1)
    # a[0] = 1 iff constraint satisfied
    qc.cx(p[0], a[0])
    qc.cx(p[1], a[0])
    qc.x(a[0])
    
    # Constraint 1: cell_1 (bits p[2], p[3]) must decode to value 2
    # Value is 2 iff b0=0 and b1=1, i.e., NOT p[2] AND p[3]
    # a[1] = 1 iff constraint satisfied
    qc.cx(p[3], a[1])
    qc.ccx(p[2], a[1], a[4])
    qc.cx(a[4], a[1])
    qc.ccx(p[2], a[1], a[4])
    
    # Constraint 2: cell_2 (bits p[4], p[5]) must decode to value 0
    # Value is 0 iff b0 = b1, i.e., NOT(b0 XOR b1)
    # a[2] = 1 iff constraint satisfied
    qc.cx(p[4], a[2])
    qc.cx(p[5], a[2])
    qc.x(a[2])
    
    # Constraint 3: cell_3 (bits p[6], p[7]) must decode to value 1
    # Value is 1 iff b0=1 and b1=0, i.e., p[6] AND NOT p[7]
    # a[3] = 1 iff constraint satisfied
    qc.cx(p[6], a[3])
    qc.ccx(p[7], a[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(p[7], a[3], a[5])
    
    # === APPLY PHASE ===
    # Apply phase -1 iff all constraints are 1
    qc.mcp(math.pi, [a[0], a[1], a[2]], a[3])
    
    # === UNCOMPUTE ALL CONSTRAINTS ===
    
    # Uncompute constraint 3 (reverse order)
    qc.ccx(p[7], a[3], a[5])
    qc.cx(a[5], a[3])
    qc.ccx(p[7], a[3], a[5])
    qc.cx(p[6], a[3])
    
    # Uncompute constraint 2
    qc.x(a[2])
    qc.cx(p[5], a[2])
    qc.cx(p[4], a[2])
    
    # Uncompute constraint 1
    qc.ccx(p[2], a[1], a[4])
    qc.cx(a[4], a[1])
    qc.ccx(p[2], a[1], a[4])
    qc.cx(p[3], a[1])
    
    # Uncompute constraint 0
    qc.x(a[0])
    qc.cx(p[1], a[0])
    qc.cx(p[0], a[0])
