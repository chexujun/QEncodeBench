qc = QuantumCircuit(len(s))
for qubit, bit in enumerate(reversed(s)):
    if bit == "1":
        qc.x(qubit)
return qc
