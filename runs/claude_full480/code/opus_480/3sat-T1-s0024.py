from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c0, c1, c2, c3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    phase = ancilla_qubits[4]

    # Clause 0: (NOT x0 OR NOT x1 OR NOT x2) -> false only when x0=x1=x2=1
    # c0 = 1 iff clause satisfied. Violated iff all three are 1.
    qc.ccx(x0, x1, c0)
    qc.ccx(c0, x2, phase)  # temporarily reuse? no - keep separate
    # Undo that (we only wanted to test); instead compute violation flag properly.
    qc.ccx(c0, x2, phase)  # cancel previous
    qc.ccx(x0, x1, c0)     # restore c0 to 0
    # c0 now back to 0. Compute clause-0-satisfied flag directly:
    # satisfied = NOT(x0 AND x1 AND x2). We'll set c0 = (x0 AND x1 AND x2) then use NOT via control-on-zero later.

    # Compute the three AND terms needed as clause-violation indicators.
    # Clause 0 violated iff x0 & x1 & x2.
    qc.ccx(x0, x1, c0)          # tmp = x0 & x1
    qc.ccx(c0, x2, c1)         # c1 = x0 & x1 & x2  (clause0 violation)
    qc.ccx(x0, x1, c0)          # uncompute tmp -> c0 back to 0

    # Clause 1: (x0 OR NOT x1 OR NOT x2) violated iff x0=0, x1=1, x2=1
    qc.x(x0)
    qc.ccx(x0, x1, c0)          # tmp = (NOT x0) & x1
    qc.ccx(c0, x2, c2)         # c2 = (NOT x0) & x1 & x2 (clause1 violation)
    qc.ccx(x0, x1, c0)          # uncompute tmp
    qc.x(x0)

    # Clause 2: (x0 OR NOT x1 OR x2) violated iff x0=0, x1=1, x2=0
    qc.x(x0)
    qc.x(x2)
    qc.ccx(x0, x1, c0)          # tmp = (NOT x0) & x1
    qc.ccx(c0, x2, c3)         # c3 = (NOT x0) & x1 & (NOT x2) (clause2 violation)
    qc.ccx(x0, x1, c0)          # uncompute tmp
    qc.x(x2)
    qc.x(x0)

    # Clause 3: (x0 OR x1 OR NOT x2) violated iff x0=0, x1=0, x2=1
    # Reuse c0 as another violation flag after building it; but c0 free now.
    qc.x(x0)
    qc.x(x1)
    qc.ccx(x0, x1, c0)          # tmp/flag build into a scratch: need a scratch qubit.
    # c0 = (NOT x0) & (NOT x1). Combine with x2 into phase directly at end.
    # We now have violation flags: c1, c2, c3 and partial (c0 & x2) for clause3.
    # f = 1 iff NO clause violated: all flags 0 AND not(c0 & x2).
    # Compute clause3 violation into a fresh combination: we need c0 & x2.
    # Use phase qubit path: mark f via multi-controlled on all-zero of violations.

    # Turn c1,c2,c3 into "clause satisfied" (=NOT violated) by X.
    qc.x(c1)
    qc.x(c2)
    qc.x(c3)
    # clause3 satisfied indicator: NOT(c0 & x2). Build c3v = c0 & x2 into phase-scratch? use X trick.
    # Multi-controlled: satisfied-all requires c1=c2=c3=1 and (c0 & x2)=0.
    # Controls: c1, c2, c3 (positive), and require NOT(c0 AND x2).
    # Implement: apply Z on... use mcx into phase with controls c1,c2,c3 and anti-control on (c0&x2).
    # First negate: we want phase -1 when satisfied. Do controlled-Z equivalent.

    # Build (c0 & x2) into a scratch = we can use the phase qubit is |0>; put g = c0 & x2 there is not allowed as control simultaneously. Instead compute g into c0? c0 holds NOT x0 & NOT x1 already.
    # Compute g = c0 & x2 into phase qubit:
    qc.ccx(c0, x2, phase)       # phase-qubit = clause3 violation g
    qc.x(phase)                 # phase-qubit = clause3 satisfied
    # Now all-satisfied iff c1=c2=c3=phase=1. Apply phase -1 via multi-controlled Z.
    qc.h(c1)
    qc.mcx([c2, c3, phase], c1)
    qc.h(c1)
    # Uncompute phase qubit
    qc.x(phase)
    qc.ccx(c0, x2, phase)
    # Restore c0
    qc.ccx(x0, x1, c0)
    qc.x(x1)
    qc.x(x0)
    # Undo satisfied-negations
    qc.x(c3)
    qc.x(c2)
    qc.x(c1)

    # Uncompute clause2 violation c3
    qc.x(x0)
    qc.x(x2)
    qc.ccx(x0, x1, c0)
    qc.ccx(c0, x2, c3)
    qc.ccx(x0, x1, c0)
    qc.x(x2)
    qc.x(x0)

    # Uncompute clause1 violation c2
    qc.x(x0)
    qc.ccx(x0, x1, c0)
    qc.ccx(c0, x2, c2)
    qc.ccx(x0, x1, c0)
    qc.x(x0)

    # Uncompute clause0 violation c1
    qc.ccx(x0, x1, c0)
    qc.ccx(c0, x2, c1)
    qc.ccx(x0, x1, c0)
