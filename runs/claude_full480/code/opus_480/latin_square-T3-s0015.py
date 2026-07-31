from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Grid layout (rows x cols), givens and free-cell qubit codes.
    # Free cells in order: (0,1),(0,2),(1,0),(1,2)
    # Cell j: b0 = problem_qubits[2j], b1 = problem_qubits[2j+1], code c = b0 + 2*b1
    # Decode: 00->0, 01->1, 10->2, 11->0  (surjective)
    #
    # Grid values:
    #   (0,0)=2 given, (0,1)=F0, (0,2)=F1
    #   (1,0)=F2,      (1,1)=2 given, (1,2)=F3
    #   (2,0)=0 given, (2,1)=1 given, (2,2)=2 given
    #
    # f(x)=1 iff the completed grid is a valid Latin square.

    F0 = (problem_qubits[0], problem_qubits[1])
    F1 = (problem_qubits[2], problem_qubits[3])
    F2 = (problem_qubits[4], problem_qubits[5])
    F3 = (problem_qubits[6], problem_qubits[7])

    # ancillas
    an = list(ancilla_qubits)
    # We'll allocate value-indicator ancillas as needed via a helper stack.

    # Helper: emit MCX with a list of (qubit, want_value) controls onto target.
    # want_value=1 -> control on |1>, want_value=0 -> control on |0> (X-conjugate).
    def mcx_pattern(controls, target):
        flips = [q for (q, v) in controls if v == 0]
        for q in flips:
            qc.x(q)
        ctrl_qubits = [q for (q, _) in controls]
        if len(ctrl_qubits) == 0:
            qc.x(target)
        elif len(ctrl_qubits) == 1:
            qc.cx(ctrl_qubits[0], target)
        elif len(ctrl_qubits) == 2:
            qc.ccx(ctrl_qubits[0], ctrl_qubits[1], target)
        else:
            qc.mcx(ctrl_qubits, target)
        for q in flips:
            qc.x(q)

    # Predicate "cell equals value" in terms of (b0,b1):
    #   val==0  <-> (00 or 11) <-> b0==b1
    #   val==1  <-> (01)       <-> b0==1 and b1==0
    #   val==2  <-> (10)       <-> b0==0 and b1==1
    #
    # Build list of "compute predicate P into ancilla a" instruction sets.
    # Each returns a callable pair (compute, uncompute).

    def eq_val_controls(cell, val):
        b0, b1 = cell
        if val == 1:
            return [(b0, 1), (b1, 0)]
        if val == 2:
            return [(b0, 0), (b1, 1)]
        raise ValueError

    # For val==0 we need b0==b1 which is not a single AND-pattern; handle specially.

    # ---- Strategy ----
    # The grid is valid iff ALL constraints hold. We compute the AND of all
    # constraint-satisfied bits into one final "all_good" ancilla, phase it,
    # then uncompute.
    #
    # Rather than enumerate solutions, we encode each pairwise/among constraint.
    #
    # Constraints (all-different) reduce, given the fixed givens, to:
    #
    # Row 0: {2, F0, F1} distinct and = {0,1,2}  => F0,F1 in {0,1}, F0!=F1, neither =2
    #        i.e. {F0,F1} = {0,1}.
    # Row 1: {F2, 2, F3} distinct => F2,F3 in {0,1}, F2!=F3 => {F2,F3}={0,1}.
    # Row 2: given, fine.
    # Col 0: {2, F2, 0} distinct => F2 = 1.
    # Col 1: {F0, 2, 1} distinct => F0 = 0.
    # Col 2: {F1, F3, 2} distinct => F1,F3 in {0,1}, F1!=F3 => {F1,F3}={0,1}.
    #
    # Solve: Col0 => F2=1. Col1 => F0=0.
    # Row0 {F0,F1}={0,1}, F0=0 => F1=1.
    # Row1 {F2,F3}={0,1}, F2=1 => F3=0.
    # Col2 {F1,F3}={0,1}: F1=1,F3=0 -> {1,0} OK. Consistent.
    #
    # UNIQUE solution: F0=0, F1=1, F2=1, F3=0.
    #
    # But because decoding is surjective (code 11 -> 0), the marked set in code
    # space is: F0 in {00,11}, F1 == 01, F2 == 01, F3 in {00,11}.
    #
    # So predicate:
    #   (F0==0) AND (F1==1) AND (F2==1) AND (F3==0)
    # where ==0 means code in {00,11} (b0==b1), ==1 means code==01.

    # Compute indicator ancillas:
    #   a0 = [F0 b0==b1]
    #   a1 = [F1 == 1]  (b0=1,b1=0)
    #   a2 = [F2 == 1]
    #   a3 = [F3 b0==b1]
    # then AND them into a final ancilla, Z, uncompute.

    a0, a1, a2, a3, aAB, aFinal = an[0], an[1], an[2], an[3], an[4], an[5]

    # ---- compute a0 = (F0 b0==b1) ----
    # b0==b1  <=>  NOT(b0 XOR b1).
    # Compute XOR into a0, then X to invert -> a0 = 1 iff equal.
    def compute_eq_bits(cell, a):
        b0, b1 = cell
        qc.cx(b0, a)
        qc.cx(b1, a)
        qc.x(a)  # a = 1 iff b0==b1

    def uncompute_eq_bits(cell, a):
        b0, b1 = cell
        qc.x(a)
        qc.cx(b1, a)
        qc.cx(b0, a)

    # ---- compute a == specific pattern into ancilla ----
    def compute_pattern(cell, val, a):
        ctrls = eq_val_controls(cell, val)
        mcx_pattern(ctrls, a)

    def uncompute_pattern(cell, val, a):
        ctrls = eq_val_controls(cell, val)
        mcx_pattern(ctrls, a)  # self-inverse

    # Compute all four indicators.
    compute_eq_bits(F0, a0)
    compute_pattern(F1, 1, a1)
    compute_pattern(F2, 1, a2)
    compute_eq_bits(F3, a3)

    # AND them: aAB = a0 AND a1 ; aFinal = aAB AND a2 AND a3.
    qc.ccx(a0, a1, aAB)
    qc.mcx([aAB, a2, a3], aFinal)

    # Phase.
    qc.z(aFinal)

    # Uncompute (mirror).
    qc.mcx([aAB, a2, a3], aFinal)
    qc.ccx(a0, a1, aAB)

    uncompute_eq_bits(F3, a3)
    uncompute_pattern(F2, 1, a2)
    uncompute_pattern(F1, 1, a1)
    uncompute_eq_bits(F0, a0)
