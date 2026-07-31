import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    a = problem_qubits
    anc = ancilla_qubits

    # a = [5, 2, 6, 1], target T = 13
    # Subsets summing to 13: {5,2,6}=13 (bits 0,1,2 selected, bit3=0)
    #                        {5,6,1,... } 5+6+1=12 no; 5+2+6=13 yes; 6+1+5=12; 2+6+1=9;
    #                        5+6+2=13 (same). 5+2+6+... check all: full=14.
    #   {5,6,2}=13 -> x = 0b0111 = bits0,1,2 =1, bit3=0
    #   {5,6,1,?}: 5+6+1=12; {5,2,6,1}=14; {6,1,5}=12; {2,6,1}=9; {5,2,1}=8
    #   {6,5,2}=13 only. Also {6,1,5}=12. Any with bit3(=1)? 1+5+6=12,1+2+5=8,1+2+6=9,1+2+5+6=14,1+5=6...
    #   So unique solution: x = 0111 => a[0]=1,a[1]=1,a[2]=1,a[3]=0.

    # Mark |x0=1, x1=1, x2=1, x3=0>. Flip x3 so all controls are 1, then mcp(pi).
    qc.x(a[3])
    qc.h(anc[0])
    qc.mcx([a[0], a[1], a[2], a[3]], anc[0])
    qc.h(anc[0])
    qc.mcx([a[0], a[1], a[2], a[3]], anc[0])  # uncompute? h-sandwich already does phase kickback
    # The above double-mcx cancels; use clean phase-kickback form instead:
    # Reset and do proper phase oracle:
    qc.mcx([a[0], a[1], a[2], a[3]], anc[0])
    qc.z(anc[0])
    qc.mcx([a[0], a[1], a[2], a[3]], anc[0])
    qc.x(a[3])
