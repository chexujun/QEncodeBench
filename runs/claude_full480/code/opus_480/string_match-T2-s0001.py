from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    # Pattern "??001": position0='?', position1='?', position2='0', position3='0', position4='1'
    # Only positions 2,3,4 are constrained. For offset o, the text bits compared are
    # s_(o+2)=0, s_(o+3)=0, s_(o+4)=1.  Offsets o in {0,1,2}.
    pattern = ['?', '?', '0', '0', '1']
    offsets = [0, 1, 2]

    n_off = len(offsets)
    # Ancilla layout: one ancilla per offset to hold that offset's match bit,
    # plus one final ancilla to OR them together for the phase.
    off_anc = ancilla_qubits[:n_off]        # 3 ancillas
    or_anc = ancilla_qubits[n_off]          # 1 ancilla

    def constrained(o):
        pairs = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            pairs.append((o + i, ch))
        return pairs

    # Compute each offset's match into its ancilla via multi-controlled X.
    # Match(o) == AND over constrained positions of (s_j == required bit).
    # Use X on qubits that require 0 so that all controls are on |1> when matched.
    for k, o in enumerate(offsets):
        pairs = constrained(o)
        ctrls = [problem_qubits[j] for (j, b) in pairs]
        for (j, b) in pairs:
            if b == '0':
                qc.x(problem_qubits[j])
        qc.mcx(ctrls, off_anc[k])
        for (j, b) in pairs:
            if b == '0':
                qc.x(problem_qubits[j])

    # OR the offset match bits into or_anc:
    # or_anc = 1 iff any off_anc[k] == 1.
    # Compute NOT(OR) then flip: set or_anc, for the all-zero case keep it 0.
    # Use: X all off_anc, mcx(off_anc -> or_anc) gives AND of negations = NOR,
    # then X or_anc to get OR, then undo X on off_anc.
    for k in range(n_off):
        qc.x(off_anc[k])
    qc.mcx(off_anc, or_anc)
    qc.x(or_anc)
    for k in range(n_off):
        qc.x(off_anc[k])

    # Phase: -1 iff or_anc == 1.
    qc.z(or_anc)

    # Uncompute OR (mirror).
    for k in range(n_off):
        qc.x(off_anc[k])
    qc.x(or_anc)
    qc.mcx(off_anc, or_anc)
    for k in range(n_off):
        qc.x(off_anc[k])

    # Uncompute each offset match (mirror).
    for k, o in enumerate(offsets):
        pairs = constrained(o)
        ctrls = [problem_qubits[j] for (j, b) in pairs]
        for (j, b) in pairs:
            if b == '0':
                qc.x(problem_qubits[j])
        qc.mcx(ctrls, off_anc[k])
        for (j, b) in pairs:
            if b == '0':
                qc.x(problem_qubits[j])
