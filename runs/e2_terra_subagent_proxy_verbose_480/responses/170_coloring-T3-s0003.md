```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # The graph constraints are equivalent to:
    #   color(2) = color(3) = color(4), and
    #   colors(0), colors(1), colors(2) are all distinct.
    eq23, eq24, distinct012, _unused = ancilla_qubits

    # Each decoded color's possible two-bit encodings, ordered (low, high).
    encodings = {
        0: ((0, 0), (1, 1)),
        1: ((1, 0),),
        2: ((0, 1),),
    }

    def toggle_on_codes(target, vertices, codes):
        """XOR target with the conjunction of the requested decoded codes."""
        controls = []
        zero_controls = []
        for vertex, code in zip(vertices, codes):
            low = problem_qubits[2 * vertex]
            high = problem_qubits[2 * vertex + 1]
            controls.extend((low, high))
            if code[0] == 0:
                zero_controls.append(low)
            if code[1] == 0:
                zero_controls.append(high)

        for qubit in zero_controls:
            qc.x(qubit)
        qc.mcx(controls, target)
        for qubit in reversed(zero_controls):
            qc.x(qubit)

    def toggle_equal(target, left, right):
        # The alternatives are mutually exclusive, so XOR accumulation is OR.
        for color in (0, 1, 2):
            for left_code in encodings[color]:
                for right_code in encodings[color]:
                    toggle_on_codes(target, (left, right),
                                    (left_code, right_code))

    def toggle_all_distinct(target, first, second, third):
        # Exactly the six permutations of the three decoded colors qualify.
        for c0, c1, c2 in (
            (0, 1, 2), (0, 2, 1), (1, 0, 2),
            (1, 2, 0), (2, 0, 1), (2, 1, 0),
        ):
            for code0 in encodings[c0]:
                for code1 in encodings[c1]:
                    for code2 in encodings[c2]:
                        toggle_on_codes(
                            target, (first, second, third),
                            (code0, code1, code2)
                        )

    toggle_equal(eq23, 2, 3)
    toggle_equal(eq24, 2, 4)
    toggle_all_distinct(distinct012, 0, 1, 2)

    # Apply -1 iff all three computed predicates hold.
    qc.h(distinct012)
    qc.mcx([eq23, eq24], distinct012)
    qc.h(distinct012)

    # Uncompute every work bit.
    toggle_all_distinct(distinct012, 0, 1, 2)
    toggle_equal(eq24, 2, 4)
    toggle_equal(eq23, 2, 3)
```
