from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    pattern = "101010"
    offsets = [0, 1]

    def apply_match_flags(invert):
        # For each offset, compute a match flag into an ancilla.
        # A match at offset o requires, for every non-'?' pattern position i,
        # that s_(o+i) == pattern[i]. We encode "match" = AND of literals.
        # Compute flag = 1 iff all fixed positions agree.
        for idx, o in enumerate(offsets):
            flag = ancilla_qubits[idx]
            fixed = [(o + i, pattern[i]) for i in range(len(pattern)) if pattern[i] != '?']
            ctrl_qubits = []
            flipped = []
            for pos, ch in fixed:
                q = problem_qubits[pos]
                if ch == '0':
                    # want s == 0, so flip so that control is satisfied when s==0
                    qc.x(q)
                    flipped.append(q)
                ctrl_qubits.append(q)
            # flag = AND(controls) via MCX onto flag ancilla
            qc.mcx(ctrl_qubits, flag)
            # undo the x on '0' positions (restore problem qubits)
            for q in flipped:
                qc.x(q)

    # Compute match flags for both offsets into ancilla[0], ancilla[1]
    apply_match_flags(False)

    # Now f(x) = OR(flag0, flag1). We need phase -1 iff OR is true.
    # Use ancilla[2] as the OR result via De Morgan:
    # OR(a,b) = NOT(AND(NOT a, NOT b)).
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    qc.x(a0)
    qc.x(a1)
    qc.mcx([a0, a1], a2)   # a2 = AND(NOT flag0, NOT flag1) = NOT OR
    qc.x(a0)
    qc.x(a1)
    # a2 == 0 means match exists. Phase -1 when OR true, i.e. when a2 == 0.
    # Apply -1 iff a2 == 0: X, Z, X gives phase on |0> component.
    qc.x(a2)
    qc.z(a2)
    qc.x(a2)

    # Uncompute a2
    qc.x(a0)
    qc.x(a1)
    qc.mcx([a0, a1], a2)
    qc.x(a0)
    qc.x(a1)

    # Uncompute the match flags (mirror of apply_match_flags)
    apply_match_flags(True)
