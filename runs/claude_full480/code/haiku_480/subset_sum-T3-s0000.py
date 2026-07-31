from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Phase oracle for subset sum: mark states where sum of selected elements equals 16.
    Elements: [7, 10, 5, 3, 9]
    """
    elements = [7, 10, 5, 3, 9]
    target = 16
    
    sum_qubits = ancilla_qubits[:6]
    
    # === COMPUTE: Accumulate the subset sum into ancillas ===
    # For each element, add it to the running sum if the corresponding problem qubit is 1
    for elem_idx, elem_val in enumerate(elements):
        ctrl = problem_qubits[elem_idx]
        
        # Add elem_val bit by bit with carry propagation
        # Process each bit position of elem_val
        for bit_pos in range(6):
            if (elem_val >> bit_pos) & 1:
                # Bit at position bit_pos is 1; need to add 2^bit_pos to sum
                # Carry logic: CCX computes carry *before* we flip the bit
                if bit_pos < 5:
                    qc.ccx(ctrl, sum_qubits[bit_pos], sum_qubits[bit_pos + 1])
                # Now flip the bit
                qc.cx(ctrl, sum_qubits[bit_pos])
    
    # === PHASE: Apply phase flip if sum == target ===
    # Target 16 = 010000 in binary (little-endian: bit 4 is 1, others are 0)
    target_binary = format(target, '06b')
    
    # Flip ancilla bits where target has 0 (to make all target bits equal to 1 for the multi-controlled gate)
    for i in range(6):
        if target_binary[5 - i] == '0':
            qc.x(sum_qubits[i])
    
    # Apply multi-controlled phase (Z gate) when all qubits are in state |1>
    # mcp(theta, controls, target): apply phase theta to target when all controls are 1
    qc.mcp(math.pi, sum_qubits[:5], sum_qubits[5])
    
    # Undo the bit flips
    for i in range(6):
        if target_binary[5 - i] == '0':
            qc.x(sum_qubits[i])
    
    # === UNCOMPUTE: Reverse the sum accumulation (restore ancillas to |0>) ===
    # Process elements in reverse order to properly uncompute carries
    for elem_idx in range(len(elements) - 1, -1, -1):
        elem_val = elements[elem_idx]
        ctrl = problem_qubits[elem_idx]
        
        # Process bits in reverse order for uncomputation
        for bit_pos in range(5, -1, -1):
            if (elem_val >> bit_pos) & 1:
                # Undo the bit flip first
                qc.cx(ctrl, sum_qubits[bit_pos])
                # Then undo the carry propagation
                if bit_pos < 5:
                    qc.ccx(ctrl, sum_qubits[bit_pos], sum_qubits[bit_pos + 1])
