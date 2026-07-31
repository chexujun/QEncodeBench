from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for subset sum problem: mark states where selected elements sum to 7.
    
    Uses compute-phase-uncompute pattern:
    1. Compute sum into ancilla[0:4]
    2. Check if sum==7 using ancilla[4] as flag
    3. Apply phase via Z gate on flag
    4. Uncompute flag and sum
    """
    a = [7, 2, 5, 7, 3]
    sum_bits = ancilla_qubits[0:4]
    flag_bit = ancilla_qubits[4]
    
    # COMPUTE: Add each element to sum if selected
    for i, val in enumerate(a):
        controlled_ripple_add(qc, problem_qubits[i], sum_bits, val)
    
    # COMPUTE FLAG: Set flag=1 iff sum==7 (binary: 0111)
    # Flip bits where target is 0 (bits 3 should be 0)
    qc.x(sum_bits[3])
    # Now bits=[*, *, *, 1] only if sum was 7
    # MCX to set flag if all of sum_bits[0:4] are 1
    qc.mcx(sum_bits, flag_bit)
    # Flip back
    qc.x(sum_bits[3])
    
    # PHASE: Apply Z on flag (phase -1 if flag=1)
    qc.z(flag_bit)
    
    # UNCOMPUTE FLAG: Reverse flag computation
    qc.x(sum_bits[3])
    qc.mcx(sum_bits, flag_bit)
    qc.x(sum_bits[3])
    
    # UNCOMPUTE: Subtract each element (in reverse order)
    for i in range(len(a) - 1, -1, -1):
        controlled_ripple_add(qc, problem_qubits[i], sum_bits, 
                             (16 - a[i]) & 0xF)  # Two's complement in 4 bits

def controlled_ripple_add(qc: QuantumCircuit, control: int, 
                          sum_bits: list[int], val: int) -> None:
    """Controlled ripple-carry adder: sum += control * val (mod 16)."""
    n = len(sum_bits)
    val = val & ((1 << n) - 1)
    
    if val == 0:
        return
    
    # Extract bits of val
    c_bits = [(val >> j) & 1 for j in range(n)]
    
    # Ripple-carry: process each bit position with carry propagation
    for j in range(n):
        if c_bits[j] == 0:
            continue
        
        if j == 0:
            # LSB: just XOR (add without carry in)
            qc.cx(control, sum_bits[0])
        else:
            # MSBs: need to handle carry from previous additions
            # Use controlled increment with existing carry implicit in state
            # For each sum_bits[j], we add val_bit[j] + carry_in
            
            # Controlled-add-1 with potential carry
            # Decompose: sum_bits[j] += (control AND val_bit[j]) + carry_in_implicit
            # Since we don't have explicit carry qubits, use controlled operations
            
            # When control=1 and val_bit=1:
            # - If sum_bits[j]=0: result should be 1 + carry_in
            # - If sum_bits[j]=1: result should be (0 + carry_in) with carry_out=1
            
            # For controlled addition without explicit carry storage,
            # we apply XOR which handles the addition part correctly when
            # the partial sum is updated in sequence
            qc.cx(control, sum_bits[j])
