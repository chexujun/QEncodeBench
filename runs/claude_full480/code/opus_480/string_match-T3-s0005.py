from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern "000" of length 3 over text length 8, offsets 0..5.
    # match at offset o  <=>  s_o = s_{o+1} = s_{o+2} = 0.
    # We need f(x) = OR over o of (NOT s_o AND NOT s_{o+1} AND NOT s_{o+2}).
    # Compute per-offset match flags into ancillas 0..5, then the phase is
    # -1 iff at least one flag is 1, i.e. NOT(all flags == 0).
    #
    # Use ancilla_qubits[0..5] as the 6 offset-match flags, ancilla_qubits[6]
    # as a scratch qubit for the OR/multi-controlled phase.

    pattern = "000"
    L = len(pattern)      # 3
    offsets = range(0, 6) # 0..5

    flags = ancilla_qubits[0:6]
    scratch = ancilla_qubits[6]

    def compute_flags():
        for idx, o in enumerate(offsets):
            fq = flags[idx]
            positions = [problem_qubits[o + i] for i in range(L)
                         if pattern[i] in ('0', '1')]
            # For pattern "000" every position requires s == 0.
            # match flag = AND over positions of (NOT s).  Wildcards skipped.
            # Flip the required-0 qubits so that "0" -> "1", AND via mcx, flip back.
            zero_positions = [problem_qubits[o + i] for i in range(L)
                              if pattern[i] == '0']
            one_positions = [problem_qubits[o + i] for i in range(L)
                             if pattern[i] == '1']
            for q in zero_positions:
                qc.x(q)
            controls = zero_positions + one_positions
            if controls:
                qc.mcx(controls, fq)
            else:
                qc.x(fq)  # empty pattern trivially matches (not this case)
            for q in zero_positions:
                qc.x(q)

    # compute
    compute_flags()

    # OR of flags -> phase.  OR(flags) == NOT( AND(NOT flag) ).
    # Flip all flags so OR becomes: at least one flipped-flag is 0.
    # Easier: apply phase -1 to every state EXCEPT the all-flags-zero state.
    # Do it as: overall we want -1 iff any flag set.
    # Trick: -1 * (identity) on all, +1 back on the all-zero-flags subspace.
    # Implement: X all flags; multicontrolled-Z marks flags-all-were-set-after-flip
    #   i.e. original all-zero -> phase +1 handled by subtracting.
    # Cleanest exact diagonal: phase = -1 iff NOT(all flags zero).
    # Use scratch: compute NOR into scratch, phase, uncompute.
    for f in flags:
        qc.x(f)
    qc.mcx(flags, scratch)   # scratch = 1 iff all flags were 0 (no match)
    for f in flags:
        qc.x(f)
    # Now scratch == 1 for no-match, 0 for match.
    # We want phase -1 on match states = states with scratch == 0.
    # Apply Z-like: phase -1 on scratch==0 is equivalent to global -1 times
    # phase +1 on scratch==0... use: X scratch, then Z on scratch gives -1 when
    # scratch(after X)==1 i.e. original scratch==0 => match.  Global phase ok.
    qc.x(scratch)
    qc.z(scratch)
    qc.x(scratch)
    # uncompute scratch
    for f in flags:
        qc.x(f)
    qc.mcx(flags, scratch)
    for f in flags:
        qc.x(f)

    # uncompute flags (mirror of compute)
    compute_flags()
