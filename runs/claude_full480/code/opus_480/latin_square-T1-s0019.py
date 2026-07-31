from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells: j=0 -> (0,0), j=1 -> (2,2)
    # Cell j: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1]; code = b0 + 2*b1
    # Decode surjective: 00->0, 01->1, 10->2, 11->0
    #
    # Grid (givens):
    #   row0: (0,0)=A   1 0
    #   row1: 0 2 1
    #   row2: 1 0 (2,2)=B
    #
    # Constraints for a valid Latin square:
    # Row0 has givens {1,0}; free A must be 2  => A == 2
    # Col0 has givens {0,1}; free A must be 2  => A == 2   (consistent)
    # Row2 has givens {1,0}; free B must be 2  => B == 2
    # Col2 has givens {0,1}; free B must be 2  => B == 2   (consistent)
    #
    # So f(x)=1 iff decode(A)==2 and decode(B)==2.
    # decode==2 only for code 10 : b0=0, b1=1.
    # So condition: A: q0==0, q1==1 ; B: q2==0, q3==1.

    q0 = problem_qubits[0]  # A b0
    q1 = problem_qubits[1]  # A b1
    q2 = problem_qubits[2]  # B b0
    q3 = problem_qubits[3]  # B b1

    a0 = ancilla_qubits[0]  # A predicate: (q0==0)and(q1==1)
    a1 = ancilla_qubits[1]  # B predicate: (q2==0)and(q3==1)

    # Compute A predicate: need q0=0, q1=1 -> use x on q0 then ccx
    qc.x(q0)
    qc.ccx(q0, q1, a0)
    qc.x(q0)

    # Compute B predicate
    qc.x(q2)
    qc.ccx(q2, q3, a1)
    qc.x(q2)

    # Phase: -1 iff a0==1 and a1==1
    qc.cz(a0, a1)

    # Uncompute B predicate
    qc.x(q2)
    qc.ccx(q2, q3, a1)
    qc.x(q2)

    # Uncompute A predicate
    qc.x(q0)
    qc.ccx(q0, q1, a0)
    qc.x(q0)
