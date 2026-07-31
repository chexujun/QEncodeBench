import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [8, 7, 11, 2, 14]
    T = 18
    n = len(a)

    # Sum register width: max sum = 8+7+11+2+14 = 42 -> 6 bits (0..63)
    sum_bits = ancilla_qubits[:6]  # 6 ancillas act as the running-sum register

    # Compute: add a[i] into the sum register (controlled by problem_qubits[i])
    # using a controlled ripple-carry increment-by-constant per selected element.
    # We implement controlled add-constant via controlled bit-flips with carry
    # using MCX cascades, adding a[i] into sum_bits when problem_qubits[i]=1.

    def controlled_add_constant(ctrl, const, reg):
        # Add integer `const` into little-endian register `reg`, controlled by `ctrl`.
        # Ripple carry: for each bit position, add const bit + incoming carry.
        # Implement using the standard controlled-increment-by-constant via
        # sequential controlled additions of powers of two with carry propagation.
        for i in range(len(reg)):
            if (const >> i) & 1:
                # add 1 at position i (controlled): ripple carry upward
                # flip higher bits where all lower target bits (from i) are 1
                for j in range(len(reg) - 1, i, -1):
                    controls = [ctrl] + reg[i:j]
                    qc.mcx(controls, reg[j])
                qc.cx(ctrl, reg[i])

    def controlled_sub_constant(ctrl, const, reg):
        # Inverse of controlled_add_constant.
        for i in range(len(reg)):
            if (const >> i) & 1:
                qc.cx(ctrl, reg[i])
                for j in range(i + 1, len(reg)):
                    controls = [ctrl] + reg[i:j]
                    qc.mcx(controls, reg[j])

    # Compute total selected sum into sum_bits
    for i in range(n):
        controlled_add_constant(problem_qubits[i], a[i], sum_bits)

    # Phase: -1 iff sum register == T (18 = 0b010010, little-endian bits: 010010)
    # Bits of 18: bit0=0,bit1=1,bit2=0,bit3=0,bit4=1,bit5=0
    Tbits = [(T >> k) & 1 for k in range(len(sum_bits))]
    for k in range(len(sum_bits)):
        if Tbits[k] == 0:
            qc.x(sum_bits[k])
    # multi-controlled Z on all sum bits -> phase -1 when all are |1>, i.e. sum==T
    qc.h(sum_bits[-1])
    qc.mcx(sum_bits[:-1], sum_bits[-1])
    qc.h(sum_bits[-1])
    for k in range(len(sum_bits)):
        if Tbits[k] == 0:
            qc.x(sum_bits[k])

    # Uncompute the sum register (mirror, reverse order)
    for i in range(n - 1, -1, -1):
        controlled_sub_constant(problem_qubits[i], a[i], sum_bits)
