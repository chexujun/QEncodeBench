import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute clause satisfiability into ancilla bits
    # Each clause is computed as: a[i] = 1 iff clause i is satisfied
    
    # Clause 1: (NOT x1 OR NOT x3 OR x4)
    # Satisfied iff NOT(x1=1 AND x3=1 AND x4=0)
    qc.x(x[4])
    qc.mcx([x[1], x[3], x[4]], a[0])
    qc.x(x[4])
    qc.x(a[0])
    
    # Clause 2: (x0 OR x2 OR x3)
    # Satisfied iff NOT(x0=0 AND x2=0 AND x3=0)
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[1])
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[3])
    qc.x(a[1])
    
    # Clause 3: (x1 OR x3 OR NOT x4)
    # Satisfied iff NOT(x1=0 AND x3=0 AND x4=1)
    qc.x(x[1])
    qc.x(x[3])
    qc.mcx([x[1], x[3], x[4]], a[2])
    qc.x(x[1])
    qc.x(x[3])
    qc.x(a[2])
    
    # Clause 4: (NOT x0 OR NOT x2 OR x3)
    # Satisfied iff NOT(x0=1 AND x2=1 AND x3=0)
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[3])
    qc.x(x[3])
    qc.x(a[3])
    
    # Clause 5: (x0 OR x1 OR NOT x2)
    # Satisfied iff NOT(x0=0 AND x1=0 AND x2=1)
    qc.x(x[0])
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[2]], a[4])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(a[4])
    
    # Clause 6: (x1 OR NOT x2 OR NOT x3)
    # Satisfied iff NOT(x1=0 AND x2=1 AND x3=1)
    qc.x(x[1])
    qc.mcx([x[1], x[2], x[3]], a[5])
    qc.x(x[1])
    qc.x(a[5])
    
    # Apply phase -1 when all clauses are satisfied
    # mcp applies phase pi when all controls are 1
    qc.mcp(math.pi, a[1:6], a[0])
    
    # Uncompute: reverse all operations to restore ancillas to |0>
    
    # Uncompute clause 6
    qc.x(a[5])
    qc.x(x[1])
    qc.mcx([x[1], x[2], x[3]], a[5])
    qc.x(x[1])
    
    # Uncompute clause 5
    qc.x(a[4])
    qc.x(x[0])
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[2]], a[4])
    qc.x(x[0])
    qc.x(x[1])
    
    # Uncompute clause 4
    qc.x(a[3])
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[3])
    qc.x(x[3])
    
    # Uncompute clause 3
    qc.x(a[2])
    qc.x(x[1])
    qc.x(x[3])
    qc.mcx([x[1], x[3], x[4]], a[2])
    qc.x(x[1])
    qc.x(x[3])
    
    # Uncompute clause 2
    qc.x(a[1])
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[1])
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[3])
    
    # Uncompute clause 1
    qc.x(a[0])
    qc.x(x[4])
    qc.mcx([x[1], x[3], x[4]], a[0])
    qc.x(x[4])
