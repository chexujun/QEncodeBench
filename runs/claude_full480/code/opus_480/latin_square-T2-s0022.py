from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells in order: j=0 -> (1,2), j=1 -> (2,0), j=2 -> (2,2)
    # Codes: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1]
    # decode: 00->0, 01->1, 10->2, 11->0
    #
    # Grid (given):
    #   row0: 2 1 0
    #   row1: 0 2 v0      v0 at (1,2)
    #   row2: v1 0 v2     v1 at (2,0), v2 at (2,2)
    #
    # Constraints for a valid Latin square:
    #   Row1 = {0,2,v0} must be {0,1,2}  => v0 == 1
    #   Row2 = {v1,0,v2} must be {0,1,2} => {v1,v2} == {1,2}
    #   Col0 = {2,0,v1}                  => v1 == 1
    #   Col1 = {1,2,0} ok (given)
    #   Col2 = {0,v0,v2}                 => {v0,v2}={1,2}; with v0=1 => v2==2
    #   Row2 with v1=1, v2=2 -> {1,0,2} ok. Consistent.
    #
    # So f=1 iff v0==1 AND v1==1 AND v2==2.
    # decode==1 means code 01: b0=1,b1=0.
    # decode==2 means code 10: b0=0,b1=1.
    #
    # v0 (j=0): b0=q0=1, b1=q1=0
    # v1 (j=1): b0=q2=1, b1=q3=0
    # v2 (j=2): b0=q4=0, b1=q5=1

    q = problem_qubits
    # predicate bits we require:
    #   q[0]=1, q[1]=0, q[2]=1, q[3]=0, q[4]=0, q[5]=1
    # Flip the ones required to be 0 so that all become 1 under a 6-controlled gate.
    flips = [q[1], q[3], q[4]]  # required 0 -> X so control sees 1 when originally 0
    for f in flips:
        qc.x(f)

    controls = [q[0], q[1], q[2], q[3], q[4], q[5]]
    target = ancilla_qubits[0]

    # compute AND of all 6 (now all should be 1) into ancilla
    qc.mcx(controls, target, ancilla_qubits[1:], mode='v-chain')
    qc.z(target)
    qc.mcx(controls, target, ancilla_qubits[1:], mode='v-chain')

    for f in flips:
        qc.x(f)
