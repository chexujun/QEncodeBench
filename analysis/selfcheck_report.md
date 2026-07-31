# Verifier self-check report

date: 2026-07-31 02:54:59 UTC

## 1-2. Reference oracles + global-phase regression
- references checked: 84 (x3 with the two global-phase variants)

## 3. Mutant rejection (16 mutants)

| mutant | rejected | fail_reason | mark_accuracy | fools uniform screen |
|---|---|---|---|---|
| M01_drop_constraint | True | MARK_MISMATCH | 0.8750 | False |
| M02_partial_phase_flip | True | MARK_MISMATCH | 0.5000 | False |
| M03_dirty_ancilla | True | ANCILLA_DIRTY | 0.0000 | False |
| M04_wrong_polarity | True | MARK_MISMATCH | 0.7500 | False |
| M05_off_by_one_qubit | True | MARK_MISMATCH | 0.8750 | False |
| M06_missing_phase | True | MARK_MISMATCH | 0.5000 | False |
| M07_and_instead_of_or | True | MARK_MISMATCH | 0.5000 | False |
| M08_phase_pattern_error | True | MARK_MISMATCH | 0.6250 | False |
| M09_double_phase | True | MARK_MISMATCH | 0.5000 | False |
| M10_nonsurjective_comparator | True | MARK_MISMATCH | 0.8438 | False |
| M11_wrong_target | True | MARK_MISMATCH | 0.7500 | False |
| M12_wrong_k_bound | True | MARK_MISMATCH | 0.7500 | False |
| M13_basis_swap | True | BASIS_CORRUPTION | 0.8750 | True |
| M14_phased_3cycle | True | BASIS_CORRUPTION | 0.8125 | True |
| M15_rolling_window_offset | True | MARK_MISMATCH | 0.6719 | False |
| M16_satcard_counter_mixup | True | MARK_MISMATCH | 0.7344 | False |

## 4. Method agreement (A vs exhaustive vs B)
- agreement checks run: 1000

## Result
**ALL CHECKS PASSED**
