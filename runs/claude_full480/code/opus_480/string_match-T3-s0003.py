from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0000"
    n = 8
    L = len(pattern)
    offsets = list(range(0, n - L + 1))  # 0..4  -> 5 offsets

    # For each offset, an ancilla holds "match at this offset" (1 = match).
    # We compute match_o = AND over pattern positions of (s_(o+i) == pattern[i]).
    # For fixed bits: literal is s or NOT s. We flip the required qubits to 1
    # on a match, MCX into a per-offset ancilla, then unflip.

    match_ancillas = ancilla_qubits[:len(offsets)]  # 5 ancillas
    final_ancilla = ancilla_qubits[len(offsets)]     # 1 ancilla for OR

    def literal_qubits(o):
        # qubits involved and the X-flips needed so that "all controls == 1"
        # means "match". pattern has only '0' and '?' here.
        controls = []
        flips = []
        for i, c in enumerate(pattern):
            q = problem_qubits[o + i]
            if c == '?':
                continue
            controls.append(q)
            if c == '0':
                flips.append(q)  # want value 0 -> flip so control-1 means match
        return controls, flips

    def compute_matches():
        for idx, o in enumerate(offsets):
            controls, flips = literal_qubits(o)
            for q in flips:
                qc.x(q)
            if controls:
                qc.mcx(controls, match_ancillas[idx])
            else:
                qc.x(match_ancillas[idx])
            for q in flips:
                qc.x(q)

    def uncompute_matches():
        for idx, o in enumerate(offsets):
            controls, flips = literal_qubits(o)
            for q in flips:
                qc.x(q)
            if controls:
                qc.mcx(controls, match_ancillas[idx])
            else:
                qc.x(match_ancillas[idx])
            for q in flips:
                qc.x(q)

    # OR over match ancillas: f = OR(match_o).
    # Compute NOR into final_ancilla, then phase.
    # De Morgan: OR = NOT(AND of NOTs). Flip each match ancilla, MCX all into
    # final -> final = AND(NOT match_o) = NOR. Then Z-phase on "not NOR".
    compute_matches()

    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final_ancilla)  # final = 1 iff no match
    for a in match_ancillas:
        qc.x(a)

    # We want phase -1 iff f==1 (at least one match) iff final_ancilla==0.
    # Apply Z on final_ancilla after X so that |final=0> gets the -1.
    qc.x(final_ancilla)
    qc.z(final_ancilla)
    qc.x(final_ancilla)

    # Uncompute final_ancilla
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, final_ancilla)
    for a in match_ancillas:
        qc.x(a)

    uncompute_matches()
