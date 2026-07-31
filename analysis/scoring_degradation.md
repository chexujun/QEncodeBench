# Scoring-regime degradation (direct rows, frozen core set)

| config | regime | degraded pass@1 | L3 pass@1 | inflation (pp) | FP rate among accepted |
|---|---|---|---|---|---|
| qwen2.5-7b (greedy) | basis16 | 27.7 | 0.0 | +27.7 | 100.0% (133/133) |
| qwen2.5-7b (greedy) | basis64 | 27.7 | 0.0 | +27.7 | 100.0% (133/133) |
| qwen2.5-7b (greedy) | super4 | 0.0 | 0.0 | +0.0 | 0.0% (0/0) |
| deepseek-v4-flash (t=0.7) | basis16 | 35.2 | 10.2 | +25.1 | 71.2% (602/846) |
| deepseek-v4-flash (t=0.7) | basis64 | 35.1 | 10.2 | +24.9 | 71.0% (598/842) |
| deepseek-v4-flash (t=0.7) | super4 | 10.3 | 10.2 | +0.1 | 1.2% (3/247) |
| deepseek-v4-flash + thinking | basis16 | 66.2 | 45.4 | +20.8 | 31.4% (100/318) |
| deepseek-v4-flash + thinking | basis64 | 66.2 | 45.4 | +20.8 | 31.4% (100/318) |
| deepseek-v4-flash + thinking | super4 | 45.4 | 45.4 | +0.0 | 0.0% (0/218) |

Ranking check: order of the three configurations under each regime vs under L3.
- basis16: deepseek-v4-flash + thinking > deepseek-v4-flash (t=0.7) > qwen2.5-7b (greedy)
- basis64: deepseek-v4-flash + thinking > deepseek-v4-flash (t=0.7) > qwen2.5-7b (greedy)
- super4: deepseek-v4-flash + thinking > deepseek-v4-flash (t=0.7) > qwen2.5-7b (greedy)
- L3: deepseek-v4-flash + thinking > deepseek-v4-flash (t=0.7) > qwen2.5-7b (greedy)
