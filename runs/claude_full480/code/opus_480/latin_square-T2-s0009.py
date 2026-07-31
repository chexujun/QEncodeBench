from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): 0->(0,1), 1->(2,0), 2->(2,1)
    # Given grid:
    #   row0: 0 . 1      free cell 0 at (0,1)
    #   row1: 2 1 0
    #   row2: . . 2      free cell 1 at (2,0), free cell 2 at (2,1)
    #
    # Value decode from 2 qubits (b0 low, b1 high): 00->0, 01->1, 10->2, 11->0.
    # value==0 iff (b0,b1) in {00,11} iff b0==b1
    # value==1 iff (b0,b1)==(1,0)
    # value==2 iff (b0,b1)==(0,1)
    #
    # Cell j: q0j=problem_qubits[2j], q1j=problem_qubits[2j+1].
    #
    # Constraints for validity:
    #  Row0: given {0,1}. free cell0 must be value 2.
    #  Row2: given {2}. free cells 1,2 must be {0,1} in some order (both != 2, and distinct).
    #  Col0: given rows0,1 = {0,2}. free cell1 (at row2,col0) must be value 1.
    #  Col1: given row1 = {1}, plus free cell0 (row0,col1) and free cell2 (row2,col1).
    #        cell0 forced to 2 (from row0). So col1 = {2 (cell0), 1(given), cell2}.
    #        cell2 must be value 0.
    #  Col2: given {1,0,2} complete.
    #  Row2 with cell1=1, cell2=0 -> {2,1,0} valid. consistent.
    #
    # So unique solution: cell0 = 2, cell1 = 1, cell2 = 0.
    #   cell0 value 2 : (b0,b1)=(0,1) -> q00=0, q10=1
    #   cell1 value 1 : (b0,b1)=(1,0) -> q01=1, q11=0
    #   cell2 value 0 : (b0,b1) in {00,11} -> q02==q12
    #
    q00, q10 = problem_qubits[0], problem_qubits[1]
    q01, q11 = problem_qubits[2], problem_qubits[3]
    q02, q12 = problem_qubits[4], problem_qubits[5]

    a = ancilla_qubits[0]   # cell0 == 2 flag
    b = ancilla_qubits[1]   # cell1 == 1 flag
    c = ancilla_qubits[2]   # cell2 == 0 flag

    # cell0 == value2 : q00==0 and q10==1  -> flip q00, then ccx
    qc.x(q00)
    qc.ccx(q00, q10, a)
    qc.x(q00)

    # cell1 == value1 : q01==1 and q11==0
    qc.x(q11)
    qc.ccx(q01, q11, b)
    qc.x(q11)

    # cell2 == value0 : q02 == q12  -> parity(q02,q12)==0
    # compute t = q02 xor q12 into c, then c==0 means equal; we want flag when equal.
    qc.cx(q02, c)
    qc.cx(q12, c)
    qc.x(c)   # now c==1 iff q02==q12

    # phase -1 iff a & b & c all 1
    qc.h(c)
    qc.ccx(a, b, c)
    qc.h(c)

    # uncompute c
    qc.x(c)
    qc.cx(q12, c)
    qc.cx(q02, c)

    # uncompute b
    qc.x(q11)
    qc.ccx(q01, q11, b)
    qc.x(q11)

    # uncompute a
    qc.x(q00)
    qc.ccx(q00, q10, a)
    qc.x(q00)
