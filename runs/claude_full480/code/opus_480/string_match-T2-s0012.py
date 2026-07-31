import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    # Pattern "0??1" over text length 5, offsets o in {0,1}.
    # Fixed constraints per offset (only non-'?' positions):
    #   pattern[0]='0', pattern[3]='1'
    # Offset o: s[o+0]==0 and s[o+3]==1.
    pattern = "0??1"
    n = 5
    offsets = [0, 1]

    # Ancilla usage: one ancilla per offset holds the match flag,
    # a final ancilla holds the OR of the offset flags.
    off_anc = [ancilla_qubits[0], ancilla_qubits[1]]  # per-offset match flags
    or_anc = ancilla_qubits[2]                          # OR accumulator

    def constraints(o):
        cons = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            cons.append((problem_qubits[o + i], ch))
        return cons

    # Compute per-offset flags: flag[o] = AND over constraints.
    # A constraint char '0' means qubit must be 0 -> X it so control sees 1.
    for idx, o in enumerate(offsets):
        cons = constraints(o)
        ctrls = []
        for q, ch in cons:
            if ch == '0':
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, off_anc[idx])

    # OR of the two flags into or_anc:
    # or = f0 OR f1 = NOT( (NOT f0) AND (NOT f1) )
    qc.x(off_anc[0])
    qc.x(off_anc[1])
    qc.mcx([off_anc[0], off_anc[1]], or_anc)
    qc.x(or_anc)
    qc.x(off_anc[0])
    qc.x(off_anc[1])

    # Phase: -1 iff or_anc == 1.
    qc.z(or_anc)

    # Uncompute OR (mirror).
    qc.x(off_anc[0])
    qc.x(off_anc[1])
    qc.x(or_anc)
    qc.mcx([off_anc[0], off_anc[1]], or_anc)
    qc.x(off_anc[1])
    qc.x(off_anc[0])

    # Uncompute per-offset flags (mirror).
    for idx, o in enumerate(offsets):
        cons = constraints(o)
        ctrls = []
        for q, ch in cons:
            ctrls.append(q)
        qc.mcx(ctrls, off_anc[idx])
        for q, ch in cons:
            if ch == '0':
                qc.x(q)
