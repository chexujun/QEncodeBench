from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: (0,1) = cell0, (1,1) = cell1.
    # Grid:
    #  row0: 0 [c0] 2
    #  row1: 2 [c1] 1
    #  row2: 1  2   0
    # Constraints for a valid Latin square:
    #   col1 must be {0,1,2} with row2 col1 = 2, so {c0,c1} = {0,1} in some order.
    #   row0 has {0,2} given -> c0 must be 1.
    #   row1 has {2,1} given -> c1 must be 0.
    # Therefore the UNIQUE solution is c0 = 1, c1 = 0.
    #
    # Codes (b0 low, b1 high), surjective decode: 00->0,01->1,10->2,11->0.
    # cell0 value 1 <=> code 01 <=> b0=1,b1=0.
    # cell1 value 0 <=> code 00 or 11 <=> b0==b1.
    #
    # Predicate f = (c0b0==1) AND (c0b1==0) AND (c1b0==c1b1).

    c0b0 = problem_qubits[0]
    c0b1 = problem_qubits[1]
    c1b0 = problem_qubits[2]
    c1b1 = problem_qubits[3]
    a_eq = ancilla_qubits[0]   # holds (c1b0 == c1b1)

    # Compute a_eq = NOT(c1b0 XOR c1b1)
    qc.cx(c1b0, a_eq)
    qc.cx(c1b1, a_eq)
    qc.x(a_eq)

    # Prepare controls so that all-ones <=> f==1:
    # need c0b0 == 1, c0b1 == 0 (flip), a_eq == 1.
    qc.x(c0b1)

    # Multi-controlled Z phase on (c0b0, c0b1(flipped), a_eq)
    qc.h(a_eq)
    qc.ccx(c0b0, c0b1, a_eq)
    qc.h(a_eq)

    # Uncompute
    qc.x(c0b1)
    qc.x(a_eq)
    qc.cx(c1b1, a_eq)
    qc.cx(c1b0, a_eq)
