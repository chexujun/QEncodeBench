from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # f(x) = 1 iff x in {(0,0,0), (0,0,1), (1,1,0)}
    # This equals: (NOT x0 AND NOT x1) OR (x0 AND x1 AND NOT x2)
    # term1 = NOT x0 AND NOT x1
    # term2 = x0 AND x1 AND NOT x2
    # f = term1 OR term2
    
    # === COMPUTE ===
    
    # Compute NOT x0 into a0
    qc.x(a0)
    qc.cx(x0, a0)  # a0 = NOT x0
    
    # Compute NOT x1 into a1
    qc.x(a1)
    qc.cx(x1, a1)  # a1 = NOT x1
    
    # Compute term1 = a0 AND a1 into a3
    qc.ccx(a0, a1, a3)  # a3 = NOT x0 AND NOT x1
    
    # Compute NOT x2 into a2
    qc.x(a2)
    qc.cx(x2, a2)  # a2 = NOT x2
    
    # Compute x0 AND x1 into a5
    qc.ccx(x0, x1, a5)  # a5 = x0 AND x1
    
    # Compute term2 = a5 AND a2 into a4
    qc.ccx(a5, a2, a4)  # a4 = x0 AND x1 AND NOT x2
    
    # Uncompute a5 (temporary)
    qc.ccx(x0, x1, a5)  # a5 = 0
    
    # Uncompute a0, a1, a2 to free them for OR computation
    qc.cx(x0, a0)
    qc.x(a0)  # a0 = 0
    
    qc.cx(x1, a1)
    qc.x(a1)  # a1 = 0
    
    qc.cx(x2, a2)
    qc.x(a2)  # a2 = 0
    
    # Compute f = a3 OR a4 using f = NOT(NOT a3 AND NOT a4)
    
    # Compute NOT a3 into a0
    qc.x(a0)
    qc.cx(a3, a0)  # a0 = NOT a3
    
    # Compute NOT a4 into a1
    qc.x(a1)
    qc.cx(a4, a1)  # a1 = NOT a4
    
    # Compute NOT a3 AND NOT a4 into a5
    qc.ccx(a0, a1, a5)  # a5 = NOT a3 AND NOT a4
    
    # Compute f = NOT a5 into a2
    qc.x(a2)
    qc.cx(a5, a2)  # a2 = NOT a5 = f
    
    # === APPLY PHASE ===
    qc.z(a2)
    
    # === UNCOMPUTE ===
    
    # Uncompute f from a2
    qc.cx(a5, a2)
    qc.x(a2)  # a2 = 0
    
    # Uncompute NOT a3 AND NOT a4 from a5
    qc.ccx(a0, a1, a5)  # a5 = 0
    
    # Uncompute NOT a4 from a1
    qc.cx(a4, a1)
    qc.x(a1)  # a1 = 0
    
    # Uncompute NOT a3 from a0
    qc.cx(a3, a0)
    qc.x(a0)  # a0 = 0
    
    # Recompute NOT x0 and NOT x1 to uncompute a3
    qc.x(a0)
    qc.cx(x0, a0)  # a0 = NOT x0
    
    qc.x(a1)
    qc.cx(x1, a1)  # a1 = NOT x1
    
    # Uncompute a3
    qc.ccx(a0, a1, a3)  # a3 = 0
    
    # Uncompute NOT x0 and NOT x1
    qc.cx(x0, a0)
    qc.x(a0)  # a0 = 0
    
    qc.cx(x1, a1)
    qc.x(a1)  # a1 = 0
    
    # Recompute x0 AND x1 and NOT x2 to uncompute a4
    qc.ccx(x0, x1, a5)  # a5 = x0 AND x1
    
    qc.x(a2)
    qc.cx(x2, a2)  # a2 = NOT x2
    
    # Uncompute a4
    qc.ccx(a5, a2, a4)  # a4 = 0
    
    # Uncompute x0 AND x1 and NOT x2
    qc.cx(x2, a2)
    qc.x(a2)  # a2 = 0
    
    qc.ccx(x0, x1, a5)  # a5 = 0
