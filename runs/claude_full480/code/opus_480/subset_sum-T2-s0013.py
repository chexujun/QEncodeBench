import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [7, 10, 7, 5]
    T = 22
    n = len(a)

    # Solutions: subsets summing to 22.
    # 7+10+5 = 22 -> select indices 0,1,3  (element index 2 = 7 not selected)
    # 10+7+5 = 22 -> select indices 1,2,3
    # Enumerate combinatorially at build time via bit patterns is fine as long
    # as we realize each solution as a multi-controlled phase (not a baked
    # brute-force LUT of gate-level solutions). We compute predicate arithmetically:
    # add selected values into an ancilla register, compare to T, phase, uncompute.

    # 4 sum-register ancillas (values up to 7+10+7+5=29 < 32 -> 5 bits needed).
    # We only have 5 ancillas; sum can reach 29 which needs 5 bits.
    s = ancilla_qubits[:5]  # sum register, little-endian, 5 bits, holds 0..29

    def add_constant(circuit, value, reg):
        # Add classical constant `value` into little-endian qubit register `reg`
        # using ripple carry via multi-controlled X (increment-by-weight).
        # Implement addition of constant by adding each set bit with carry
        # using the standard "add a power of two with carry propagation".
        for bit in range(len(reg)):
            if (value >> bit) & 1:
                # add 1 at position `bit`: increment reg from position bit upward
                for j in range(len(reg) - 1, bit, -1):
                    # carry into position j requires all lower controls from bit..j-1
                    circuit.mcx(reg[bit:j], reg[j])
                circuit.x(reg[bit])

    # compute: conditionally add a[i] when problem_qubits[i] == 1.
    # controlled constant addition: gate each add-step with the selection qubit.
    def controlled_add_constant(circuit, ctrl, value, reg, work):
        # Use one extra... but we have no spare ancilla. Instead, control every
        # mcx/x in add_constant on ctrl by extending control list.
        for bit in range(len(reg)):
            if (value >> bit) & 1:
                for j in range(len(reg) - 1, bit, -1):
                    circuit.mcx([ctrl] + reg[bit:j], reg[j])
                circuit.mcx([ctrl], reg[bit])

    # compute sum
    for i in range(n):
        controlled_add_constant(qc, problem_qubits[i], a[i], s)

    # phase: -1 iff sum == T. T=22 = 10110b -> bits: b0=0,b1=1,b2=1,b3=0,b4=1
    tbits = [(T >> k) & 1 for k in range(5)]
    for k in range(5):
        if tbits[k] == 0:
            qc.x(s[k])
    # multi-controlled Z on all 5 sum bits
    qc.h(s[4])
    qc.mcx(s[:4], s[4])
    qc.h(s[4])
    for k in range(5):
        if tbits[k] == 0:
            qc.x(s[k])

    # uncompute sum (reverse controlled additions)
    def controlled_add_constant_inv(circuit, ctrl, value, reg):
        for bit in range(len(reg)):
            if (value >> bit) & 1:
                circuit.mcx([ctrl], reg[bit])
                for j in range(bit + 1, len(reg)):
                    circuit.mcx([ctrl] + reg[bit:j], reg[j])

    for i in range(n - 1, -1, -1):
        controlled_add_constant_inv(qc, problem_qubits[i], a[i], s)
