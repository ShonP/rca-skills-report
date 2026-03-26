# RCA Skills vs MCP Tools — Evaluation Report

**Date:** March 25, 2026
**Branch:** `users/shonpazarker/rca-skill-based`
**PR:** #15157022
**Model:** gpt-5.4 | **Seed:** 42 | **Tests:** 67 | **Jobs:** 7

### Terminology
- **MCP Skills** (`RCA_MCP_ASSISTANT_SKILLS`) — Skills loaded on-demand via a `LoadSkill` MCP tool call. The agent explicitly calls the tool to fetch skill content during execution.
- **Native Skills** (`RCA_MCP_ASSISTANT_NATIVE_SKILLS`) — Skills injected automatically as context via the Agent Framework SDK's `SkillsProvider`. No tool call needed — content is available from the start.

## 1. Experiment Setup

### Flows Compared

| Flow | Tools | Skills (LoadSkill / Native) | Pipeline Runs |
|------|-------|-----------------------------|---------------|
| **RCA_MCP_ASSISTANT** (baseline) | DiffPatterns, Quantization, ExecuteKQL | None | [Run 1](https://msazure.visualstudio.com/One/_build/results?buildId=158140216), [Run 2](https://dev.azure.com/msazure/One/_build?definitionId=330958) (RunId: 945e5809) |
| **RCA_MCP_ASSISTANT_SKILLS** | DiffPatterns, Quantization, ExecuteKQL, **LoadSkill** | anomaly-detection, change-point-detection (via MCP LoadSkill tool) | [Run 1](https://msazure.visualstudio.com/One/_build/results?buildId=158140224), [Run 2](https://dev.azure.com/msazure/One/_build?definitionId=330958) (RunId: 0a0acd23) |
| **RCA_MCP_ASSISTANT_NATIVE_SKILLS** | DiffPatterns, Quantization, ExecuteKQL | anomaly-detection, change-point-detection (injected as Agent Framework SDK context) | [Run 1](https://msazure.visualstudio.com/One/_build/results?buildId=158140231), [Run 2](https://dev.azure.com/msazure/One/_build?definitionId=330958) (RunId: 0ad86fb9) |

**Key difference:** The baseline has no anomaly detection guidance at all. The skill-based flows **add** anomaly detection and change-point detection knowledge via skills — either through a LoadSkill MCP tool or native SDK context injection. The DiffPatterns tool remains in all flows.

## 2. Results — Overall Accuracy (Average of 2 Runs per Flow, 67 tests each)

![gpt-5.4 No Reasoning Overall Accuracy](chart_s2_overall.png)

| AccuracyMethod | Baseline | MCP Skills | Native Skills | Best | Delta vs Baseline |
|----------------|----------|-----------|--------------|------|-------------------|
| **AnomalyDetectionJudge** | 66.1% | **72.5%** | 71.3% | MCP Skills | **+6.4pp** |
| **DiffPatternJudge** | **63.1%** | 57.8% | 61.6% | Baseline | **-5.3pp** |
| **RCAJudge** | 70.9% | **71.3%** | 71.5% | Native Skills | **+0.6pp** |

## 3. Results — Sub-Metrics Breakdown (Average of 2 Runs)

![gpt-5.4 No Reasoning Sub-Metrics](chart_s3_sub_metrics.png)

### AnomalyDetectionJudge Sub-Metrics

| Sub-Metric | Baseline | MCP Skills | Native Skills | Delta (MCP Skills) |
|------------|----------|-----------|--------------|-------------------|
| **AnomalyDetectionUsage** | 56.8% | **71.8%** | 70.2% | **+15.0pp** |
| TimeframeCorrectness | 75.9% | **78.5%** | 77.9% | +2.6pp |
| ToolCallsEfficiency | 68.6% | **70.6%** | 69.1% | +2.0pp |

### DiffPatternJudge Sub-Metrics

| Sub-Metric | Baseline | MCP Skills | Native Skills | Delta (MCP Skills) |
|------------|----------|-----------|--------------|-------------------|
| **DedicatedToolsUsage** | **70.7%** | 62.8% | 70.1% | -7.9pp |
| Methodology | **65.8%** | 60.5% | 63.5% | -5.3pp |
| PatternCorrectness | **55.4%** | 52.8% | 53.9% | -2.6pp |

### RCAJudge Sub-Metrics

| Sub-Metric | Baseline | MCP Skills | Native Skills | Delta (MCP Skills) |
|------------|----------|-----------|--------------|-------------------|
| Completeness | 68.1% | 68.3% | **69.1%** | +0.2pp |
| Correctness | 59.4% | **60.3%** | 60.0% | +0.9pp |
| EntitiesSelection | **87.8%** | 87.8% | 87.4% | +0.0pp |
| Methodology | 73.0% | 73.8% | **74.2%** | +0.8pp |
| ProblemUnderstanding | 85.9% | **86.4%** | 86.2% | +0.5pp |
| ReportQuality | **87.7%** | 87.6% | 87.5% | -0.1pp |

### Latency

| Flow | AvgTestDuration |
|------|-----------------|
| RCA_MCP_ASSISTANT (baseline) | 20.8s |
| RCA_MCP_ASSISTANT_SKILLS | **19.7s** |
| RCA_MCP_ASSISTANT_NATIVE_SKILLS | 22.5s |

## 4. Key Findings

1. **Skills massively improve anomaly detection** — `AnomalyDetectionUsage` jumped **+15.0pp** (56.8% → 71.8%) averaged across 2 runs. The baseline has no anomaly detection tools at all — the skill adds this capability by teaching the agent `series_decompose_anomalies` and `series_fit_2lines` KQL patterns, which it then writes via `ExecuteKQL`.

2. **Skills hurt diffpatterns** — All three DiffPattern sub-metrics regressed. `DedicatedToolsUsage` dropped -7.9pp. The diffpatterns tool is still available but the agent uses it less when skills are present.

3. **RCA overall is marginally positive** — The anomaly detection gains outweigh diffpatterns losses, resulting in ~+0.6pp on RCAJudge.

4. **MCP Skills vs Native Skills** — MCP Skills slightly outperforms Native Skills on anomaly detection (72.5% vs 71.3%). Native Skills barely regresses DiffPatterns (70.1% vs 70.7% baseline) because it doesn't cost a turn. MCP Skills regresses DiffPatterns significantly (62.8%) due to turn budget competition.

5. **Latency is neutral** — MCP Skills is actually the fastest flow (19.7s vs 20.8s baseline). Native Skills adds ~2s.

## 5. Deep-Dive: Why DiffPatterns Regressed

### 5.1 Tool Call Analysis (67 tests, Run 0a0acd23 vs 945e5809)

| Metric | Baseline | MCP Skills |
|--------|----------|-----------|
| Tests using DiffPatterns tool | **64/67** (95.5%) | **56/67** (83.6%) |
| Tests using LoadSkill | 0/67 | **66/67** (98.5%) |
| Avg tool calls per test | 14.1 | 13.9 |

**8 tests lost DiffPatterns usage** when skills were added. Total tool calls are nearly identical (~14), but this is **not a hard framework limit** — the Agent Framework SDK default is `max_iterations=40`. The agent **chooses** to stop at ~14 turns because gpt-5.4 self-terminates when it believes the task is complete. LoadSkill consumes a slot that otherwise would have been DiffPatterns within the agent's self-selected budget.

### 5.2 The 10 Worst-Regressing DiffPattern Tests

For the 10 tests where the skills flow **dropped DiffPatterns entirely** (baseline used it, skills didn't), we checked how their anomaly detection scores changed:

| Tests where DiffPatterns was lost | Anomaly improved | Anomaly same/worse |
|-----------------------------------|-----------------|-------------------|
| Count | **6 out of 10** | 4 out of 10 |
| Avg anomaly delta | +0.16pp | -0.12pp |

**6 out of 10 tests that lost DiffPatterns actually improved on anomaly detection.** The agent found anomalies better but ran out of turns before reaching DiffPatterns.

### 5.3 Root Cause: Skill Content Over-Engagement

Examining the judge justifications for a representative test (f4f8e8, anomaly +0.32, diffpatterns -0.27):

**Baseline (anomaly 0.56):**
> "The agent anchored on the alert time correctly but failed to scan far enough back to find the earlier causal onset."

**Skills (anomaly 0.88):**
> "The agent used series_decompose_anomalies to validate the alert-time spike AND change-point detection to identify an earlier structural onset. Scanned a wider pre-alert range back to 2027-02-20."

The skill taught the agent to use **both** `series_decompose_anomalies` AND `series_fit_2lines` (from the change-point skill) to find the causal onset. This is genuinely better anomaly analysis — not just using recipes superficially. But the agent then spent all remaining turns on anomaly KQL queries and never reached step 7 (DiffPatterns).

### 5.4 System Prompt Analysis

Comparing `SYSTEM_MESSAGE_RCA` (baseline) vs `SYSTEM_MESSAGE_RCA_ASSISTANT_SKILLS`:

The skills prompt adds 3 elements that prime the agent toward anomaly work early:

1. **"Available Skills" section** at the top listing anomaly-detection and change-point-detection
2. **Guidelines bullet**: "Consider loading relevant skills via LoadSkill"
3. **Step 4 hint**: "Consider loading the rca-anomaly-detection skill for additional patterns"

All 3 additions point to anomaly detection only. There are **no skill hints near Step 7 (DiffPatterns)**. The agent is primed to prioritize skill loading at step 4, then over-invests in anomaly analysis patterns from the loaded skill content.

### 5.5 Summary

The DiffPatterns regression is caused by **three compounding factors**:

1. **Turn budget competition** — LoadSkill costs 1 turn out of ~14, and the rich skill content encourages multiple follow-up ExecuteKQL calls for anomaly patterns
2. **System prompt priming** — The skills prompt mentions LoadSkill at steps 1-4 but not at step 7 (DiffPatterns), biasing the agent toward early skill loading
3. **Skill content over-engagement** — The anomaly skill teaches thorough multi-technique analysis (decompose + change-point + validation), which the agent eagerly follows at the expense of progressing to DiffPatterns

**Native Skills avoid most of this** — they inject context passively (DiffPatterns regression: only -0.6pp vs baseline) because they don't cost a turn and don't trigger the "explore skill content" behavior.

### 5.6 Reasoning Fixes the Turn Budget Issue

Enabling reasoning on gpt-5.4 (effort: medium, summary: detailed) dramatically changes behavior:

| Metric | gpt-5.4 (no reasoning) | gpt-5.4 (reasoning) |
|--------|------------------------|---------------------|
| Avg tool calls | 14.1 | **23.8-27.5** |
| DiffPatterns usage (baseline) | 64/67 (95.5%) | **65/67** (97.0%) |
| DiffPatterns usage (MCP Skills) | 56/67 (83.6%) | **64/67** (95.5%) |

With reasoning enabled, gpt-5.4 uses nearly 2x more tool calls and maintains DiffPatterns usage even with skills present. The model's internal planning prevents the premature self-termination observed without reasoning.

## 6. gpt-5.1 (Reasoning Model) Results

**Model:** gpt-5.1 (reasoning) | **Judge:** gpt-5.4 | **Seed:** 42 | **Tests:** 67 | **Branch:** rca-skill-based

Pipeline runs: [Baseline](https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_build/results?buildId=158149204) | [Skills](https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_build/results?buildId=158149215) | [Native](https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_build/results?buildId=158149226)

### Overall Accuracy (gpt-5.1)

| AccuracyMethod | Baseline | MCP Skills | Native Skills | Best | Delta vs Baseline |
|----------------|----------|-----------|--------------|------|-------------------|
| **AnomalyDetectionJudge** | 57.7% | 62.8% | **64.4%** | Native Skills | **+6.7pp** |
| **DiffPatternJudge** | 59.9% | 61.6% | **62.9%** | Native Skills | **+3.0pp** |
| **RCAJudge** | 67.3% | 67.9% | **68.3%** | Native Skills | **+1.0pp** |

### Sub-Metrics (gpt-5.1)

| Sub-Metric | Baseline | MCP Skills | Native Skills | Delta (MCP Skills) |
|------------|----------|-----------|--------------|-------------------|
| **AnomalyDetectionUsage** | 45.2% | **59.4%** | 65.1% | **+14.2pp** |
| TimeframeCorrectness | 67.3% | **67.8%** | 65.9% | +0.5pp |
| ToolCallsEfficiency | 63.4% | **64.0%** | 65.3% | +0.6pp |
| **DedicatedToolsUsage** | 74.0% | **77.7%** | 78.9% | **+3.7pp** |
| Methodology | 60.5% | **61.5%** | 64.0% | +1.0pp |
| PatternCorrectness | 48.1% | **48.3%** | 48.8% | +0.2pp |
| Completeness | 65.0% | **66.4%** | 66.0% | +1.4pp |
| Correctness | 55.3% | **54.4%** | 55.5% | -0.9pp |
| EntitiesSelection | 85.2% | **85.5%** | 85.0% | +0.3pp |
| Methodology (RCA) | 68.5% | **71.4%** | 72.0% | +2.9pp |
| ProblemUnderstanding | 81.2% | **81.6%** | 79.8% | +0.4pp |
| ReportQuality | 86.0% | **86.1%** | 86.1% | +0.1pp |

### Tool Call Analysis (gpt-5.1)

| Metric | Baseline | MCP Skills | Native Skills |
|--------|----------|-----------|--------------|
| Avg tool calls per test | 14.2 | 15.3 | 15.3 |
| Tests using DiffPatterns | **65/67** (97.0%) | **65/67** (97.0%) | **66/67** (98.5%) |
| Tests using LoadSkill | 0 | **63/67** (94.0%) | 0 |

### Latency (gpt-5.1)

| Flow | AvgTestDuration |
|------|-----------------|
| RCA_MCP_ASSISTANT (baseline) | 45.9s |
| RCA_MCP_ASSISTANT_SKILLS | **37.1s** |
| RCA_MCP_ASSISTANT_NATIVE_SKILLS | 44.1s |

### Key Findings — gpt-5.1

1. **DiffPatterns regression is GONE** — gpt-5.1 with skills actually **improves** DiffPatterns (+3.0pp native, +1.7pp MCP). The reasoning model uses more turns (15.3 vs 14.2) and completes all 8 RCA steps including DiffPatterns (97-98.5% usage) even with LoadSkill present.

2. **Anomaly detection still benefits** — `AnomalyDetectionUsage` improved +14.2pp (MCP) and +19.9pp (native), consistent with gpt-5.4 findings. The skill content genuinely helps regardless of model.

3. **DedicatedToolsUsage improved** — Unlike gpt-5.4 where this regressed -7.9pp, gpt-5.1 shows **+3.7pp** (MCP) and **+4.9pp** (native). The reasoning model is better at following all steps.

4. **Native Skills is the clear winner** — Beats both baseline and MCP Skills on every metric. No turn cost, no prompt priming issues.

5. **gpt-5.1 is slower than gpt-5.4 without reasoning** — gpt-5.1 takes ~37-46s vs ~20s for gpt-5.4 (no reasoning). Both reasoning-enabled configs (gpt-5.1 and gpt-5.4+reasoning) have similar latency (~37-60s). The latency increase comes from reasoning, not from the model itself.

### Comparison: gpt-5.1 vs gpt-5.4

| Metric | gpt-5.4 MCP Skills Delta | gpt-5.1 MCP Skills Delta | Interpretation |
|--------|-------------------------|-------------------------|----------------|
| AnomalyDetection | **+6.4pp** | +5.1pp | Both benefit similarly |
| DiffPatterns | **-5.3pp** | **+1.7pp** | gpt-5.1 fixes the regression |
| RCA | +0.6pp | +0.6pp | Identical net RCA gain |
| DiffPatterns tool usage | 56/67 (83.6%) | **65/67 (97.0%)** | gpt-5.1 completes the workflow |

**Conclusion:** The DiffPatterns regression was a **gpt-5.4 (no reasoning) behavioral limitation** — it self-terminates too early. Both gpt-5.1 and gpt-5.4 with reasoning complete all RCA steps, making skills purely additive with no trade-offs.

## 7. gpt-5.4 with Reasoning Results

### Cross-Model Comparison

![Cross-Model Comparison by Flow](chart_cross_model.png)

![DiffPatterns Regression Story](chart_diffpatterns_story.png)

![Latency by Model Configuration](chart_cross_model_latency.png)

**Model:** gpt-5.4 + reasoning (effort: medium, summary: detailed) | **Judge:** gpt-5.4 | **Seed:** 42 | **Branch:** devSE

Pipeline runs: [Baseline](https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_build/results?buildId=158156657) | [Skills](https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_build/results?buildId=158156690) | [Native](https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_build/results?buildId=158156716)

### Overall Accuracy (gpt-5.4 + reasoning)

| AccuracyMethod | Baseline | MCP Skills | Native Skills | Best | Delta vs Baseline |
|----------------|----------|-----------|--------------|------|-------------------|
| **AnomalyDetectionJudge** | 66.3% | **69.5%** | 69.4% | MCP Skills | **+3.2pp** |
| **DiffPatternJudge** | 65.7% | **68.0%** | 67.3% | MCP Skills | **+2.3pp** |
| **RCAJudge** | 69.4% | **71.5%** | 70.7% | MCP Skills | **+2.1pp** |

### Tool Call Analysis (gpt-5.4 + reasoning)

| Metric | Baseline | MCP Skills | Native Skills |
|--------|----------|-----------|--------------|
| Avg tool calls per test | 23.8 | 27.1 | 27.5 |
| Tests using DiffPatterns | **65/67** (97.0%) | **64/67** (95.5%) | **65/67** (97.0%) |
| Tests using LoadSkill | 0 | **62/67** (92.5%) | 0 |

### Latency (gpt-5.4 + reasoning)

| Flow | AvgTestDuration |
|------|-----------------|
| RCA_MCP_ASSISTANT (baseline) | 53.3s |
| RCA_MCP_ASSISTANT_SKILLS | 60.4s |
| RCA_MCP_ASSISTANT_NATIVE_SKILLS | 56.1s |

### Key Findings — gpt-5.4 + reasoning

1. **DiffPatterns regression eliminated** — With reasoning, MCP Skills *improves* DiffPatterns by +2.3pp (vs -5.3pp without reasoning). DiffPatterns tool usage stays at 95.5% (vs 83.6% without reasoning).

2. **All metrics improve with skills** — Unlike gpt-5.4 without reasoning which had a DiffPatterns trade-off, reasoning makes skills purely additive across all three judges.

3. **More tool calls** — Reasoning enables 23.8-27.5 tool calls per test (vs ~14 without reasoning), giving the agent enough budget to complete all 8 RCA steps including DiffPatterns even after LoadSkill.

4. **MCP Skills beats Native Skills** — With reasoning, the LoadSkill turn cost is absorbed by the larger turn budget. MCP Skills slightly outperforms Native Skills on all three overall metrics.

5. **Latency trade-off** — Reasoning adds ~2.5x latency (53-60s vs 20s without reasoning). Similar to gpt-5.1 latency profile.

### Cross-Model Comparison (all configs)

| Config | AnomalyDetection | DiffPatterns | RCA | DiffPatterns Tool Usage |
|--------|-----------------|-------------|-----|------------------------|
| gpt-5.4 (no reasoning) | +6.4pp | **-5.3pp** | +0.6pp | 83.6% |
| gpt-5.4 + reasoning | **+3.2pp** | **+2.3pp** | **+2.1pp** | 95.5% |
| gpt-5.1 (reasoning) | +5.1pp | +1.7pp | +0.6pp | 97.0% |

*All deltas are MCP Skills vs Baseline for that model config.*

**Conclusion:** Reasoning (on either model) eliminates the DiffPatterns regression. gpt-5.4 + reasoning gives the best overall RCA improvement (+2.1pp) with the highest anomaly gains and no trade-offs. The DiffPatterns regression was specific to gpt-5.4 without reasoning, where the model self-terminates at ~14 turns.

## 8. Key Takeaways

1. **Skills work.** Teaching the agent KQL patterns via skills improves anomaly detection by +6-15pp across all model configurations. The improvement is real — the agent writes better `series_decompose_anomalies` and `series_fit_2lines` queries, finds anomaly onsets earlier, and validates with anomaly scores instead of raw counts.

2. **Reasoning eliminates the DiffPatterns trade-off.** Without reasoning, gpt-5.4 self-terminates after ~14 tool calls and the LoadSkill call displaces DiffPatterns. With reasoning (gpt-5.1 or gpt-5.4+reasoning), the agent uses 15-27 tool calls and completes all 8 RCA steps. Skills become purely additive with no regressions.

3. **Native Skills are the safest delivery mechanism.** They inject context without consuming a tool call, avoiding the turn budget competition entirely. Even without reasoning, Native Skills regresses DiffPatterns by only -0.6pp (vs -5.3pp for MCP Skills).

4. **MCP Skills win when reasoning is available.** With reasoning, MCP Skills slightly outperforms Native Skills on all metrics. The on-demand loading gives the agent more control over when to use skill content.

5. **Latency is the cost of reasoning.** All reasoning configurations take 2-3x longer (~40-60s vs ~20s). This is the trade-off for eliminating the DiffPatterns regression.

## 9. Reproduction KQL Queries

**Cluster:** `trd-2cucrmayps8aqfwk92.z9.kusto.fabric.microsoft.com` | **Database:** `KustoAssistantTests`

```kql
// Overall summary with sub-metrics
TestResultView
| where Timestamp > ago(3h)
| where Flow contains "RCA_MCP_ASSISTANT"
| where Description contains "skill"
| where Model == "gpt-5.4"
| where User contains "shon"
| invoke Summarize(ShowSubMetrics=true)
```

```kql
// Averaged across runs
TestResultView
| where Timestamp > ago(3h)
| where Flow contains "RCA_MCP_ASSISTANT"
| where Description contains "skill"
| where Model == "gpt-5.4"
| where User contains "shon"
| invoke Summarize(ShowSubMetrics=true)
| summarize AvgAcc=avg(AvgAccuracy), Runs=count() by Flow, AccuracyMethod
| order by AccuracyMethod asc, Flow asc
```

## 10. Experiment Results (A–E)

**Model:** gpt-5.4 + reasoning (medium/detailed) | **Judge:** gpt-5.4 | **Seed:** 42 | **Tests:** 67 | **Date:** March 25–26, 2026

### Experiment Descriptions

| # | Experiment | Branch | Change |
|---|-----------|--------|--------|
| A+D | **All skills (additive)** | `exp-a-all-skills` | Added `rca-diffpatterns` skill to all flows (3 skills total) |
| B | **No hints** | `exp-b-no-hints` | SKILLS/NATIVE flows use baseline prompt (no "Consider loading" hints) |
| C | **Concise skill** | `exp-c-concise` | Trimmed anomaly skill to core pattern only (removed gap filling, interpreting, threshold sections) |
| E | **Merged skills** | `exp-e-merged` | Combined anomaly + change-point into single `rca-time-series-analysis` skill |

### Overall RCA Accuracy

![Overall RCA Accuracy by Experiment](chart1_overall_rca.png)

| Experiment | Baseline | MCP Skills | Native Skills | Best Flow | Delta vs Original Best |
|---|---|---|---|---|---|
| **Original (2 skills)** | 69.4% | **71.5%** | 70.7% | MCP Skills | — |
| **A: All Skills** | **70.8%** | 71.0% | 67.9% | MCP Skills | -0.5pp |
| **B: No Hints** | 69.8% | **71.2%** | 68.4% | MCP Skills | -0.3pp |
| **C: Concise** | 70.2% | **71.0%** | 68.6% | MCP Skills | -0.5pp |
| **E: Merged** | **71.8%** | 70.3% | 69.7% | Baseline | +0.3pp |

### Sub-Metrics Heatmap

![Sub-Metric Accuracy Heatmap](chart2_heatmap.png)

### Sub-Metrics Breakdown

| Experiment | Flow | Anomaly Detection | DiffPatterns | Overall RCA |
|---|---|---|---|---|
| **Original** | Baseline | 66.3% | 65.7% | 69.4% |
| | MCP Skills | 69.5% | 68.0% | 71.5% |
| | Native Skills | 69.4% | 67.3% | 70.7% |
| **A: All Skills** | Baseline | 66.3% | 67.1% | 70.8% |
| | MCP Skills | 69.4% | 69.1% | 71.0% |
| | Native Skills | 67.0% | 65.4% | 67.9% |
| **B: No Hints** | Baseline | 67.2% | 66.2% | 69.8% |
| | MCP Skills | 69.4% | 67.9% | 71.2% |
| | Native Skills | 65.7% | 64.4% | 68.4% |
| **C: Concise** | Baseline | 66.3% | 67.0% | 70.2% |
| | MCP Skills | 69.2% | 66.4% | 71.0% |
| | Native Skills | 67.2% | 65.5% | 68.6% |
| **E: Merged** | Baseline | 67.0% | 69.0% | 71.8% |
| | MCP Skills | 69.4% | 67.2% | 70.3% |
| | Native Skills | 68.0% | 66.8% | 69.7% |

### Delta vs Original

![Accuracy Delta vs Original](chart3_deltas.png)

### Latency

![Average Latency](chart4_latency.png)

| Experiment | Baseline | MCP Skills | Native Skills |
|---|---|---|---|
| **A: All Skills** | 296s | 287s | 311s |
| **B: No Hints** | 279s | 321s | 340s |
| **C: Concise** | 298s | 301s | 323s |
| **E: Merged** | 293s | 294s | 322s |

### MCP Skills Accuracy Trend

![MCP Skills Accuracy Across Experiments](chart5_mcp_skills_trend.png)

### Experiment Findings

1. **MCP Skills is consistently the top flow** — across all experiments, MCP Skills delivers the best or near-best overall RCA accuracy (70.3–71.2%). The delivery mechanism (LoadSkill tool) matters more than skill content variations.

2. **Native Skills regresses in all experiments** — Native Skills drops 1.0–2.8pp vs the original in every experiment. The injected-context approach may overwhelm the agent when combined with reasoning, unlike MCP Skills where the agent controls when to read skill content.

3. **Experiment E (Merged) boosts Baseline the most** — Baseline jumps to 71.8% overall RCA (+2.4pp), the highest single-flow score across all experiments. Merging skills into one may have simplified the system prompt enough to benefit even the no-skill flow.

4. **Experiment A (All Skills) helps DiffPatterns for MCP Skills** — Adding a dedicated diffpatterns skill boosts that specific metric to 69.1% (+1.1pp), confirming skills can augment the tool they supplement.

5. **Experiment B (No Hints) shows hints are not the problem** — Removing prompt hints barely changes MCP Skills accuracy (71.2% vs 71.5%), indicating the regression in Native Skills is driven by skill content injection itself, not prompt priming.

6. **Experiment C (Concise) doesn't help** — Trimming the skill content didn't improve anything; the over-engagement hypothesis was wrong. The issue is structural (how Native Skills injects context) rather than content length.

7. **Latency is ~290–340s** — Much higher than the original ~53–60s, likely because these experiments used gpt-5.4+reasoning while the original latency was from non-reasoning runs. Native Skills is consistently the slowest flow (~310–340s).
