from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [2, 15, 14, 9, 4]
    T = 9
    n = len(a)
    # Sum bits needed: max sum = 2+15+14+9+4 = 44 -> 6 bits (0..63)
    W = 6
    s = ancilla_qubits[0:W]  # 6 accumulator ancillas hold running subset sum

    def add_const(c):
        # Add classical constant c into the accumulator register s (mod 2^W),
        # controlled overall by problem qubit later; here unconditional ripple.
        pass

    # Controlled ripple-carry adder: add a[i] (classical constant) into s,
    # conditioned on problem_qubits[i]. Implemented via controlled increments
    # using an MCX carry-chain approach without extra ancillas.
    def add_const_controlled(ctrl, c, uncompute=False):
        # Add constant c into register s (W bits), controlled on ctrl.
        # Use the standard controlled ripple: process bit by bit with carries
        # realized by cascaded multi-controlled X gates.
        bits = [(c >> k) & 1 for k in range(W)]
        order = range(W)
        for k in order:
            if bits[k] == 0:
                continue
            # Adding a 1 at position k: flip s[k], carry into higher bits.
            # Ripple carry: for a constant addend, a '1' at bit k flips s[k];
            # a carry propagates while lower target bits were 1.
            # Multi-controlled X from s[k..j-1] and ctrl onto s[j], from top down
            # so controls are read before being modified.
            for j in range(W - 1, k, -1):
                controls = [ctrl] + [s[m] for m in range(k, j)]
                qc.mcx(controls, s[j])
            qc.cx(ctrl, s[k])

    def add_const_controlled_inverse(ctrl, c):
        # Exact inverse of add_const_controlled (subtract).
        bits = [(c >> k) & 1 for k in range(W)]
        for k in reversed(range(W)):
            if bits[k] == 0:
                continue
            qc.cx(ctrl, s[k])
            for j in range(k + 1, W):
                controls = [ctrl] + [s[m] for m in range(k, j)]
                qc.mcx(controls, s[j])

    # Compute subset sum into s
    for i in range(n):
        add_const_controlled(problem_qubits[i], a[i])

    # Phase flip iff s == T (compare register to constant T)
    tbits = [(T >> k) & 1 for k in range(W)]
    for k in range(W):
        if tbits[k] == 0:
            qc.x(s[k])
    qc.h(s[W - 1])
    qc.mcx(s[0:W - 1], s[W - 1])
    qc.h(s[W - 1])
    for k in range(W):
        if tbits[k] == 0:
            qc.x(s[k])

    # Uncompute subset sum
    for i in reversed(range(n)):
        add_const_controlled_inverse(problem_qubits[i], a[i])
