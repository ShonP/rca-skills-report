import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

matplotlib.use('Agg')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

COLORS = {
    'Baseline': '#4472C4',
    'MCP Skills': '#ED7D31',
    'Native Skills': '#70AD47',
}

METRICS = ['AnomalyDetectionJudge', 'DiffPatternJudge', 'RCAJudge']
METRIC_LABELS = {
    'AnomalyDetectionJudge': 'Anomaly Detection',
    'DiffPatternJudge': 'DiffPatterns',
    'RCAJudge': 'Overall RCA',
}
FLOWS = ['Baseline', 'MCP Skills', 'Native Skills']

# === Section 2-3: gpt-5.4 no reasoning (original) ===
gpt54_no_reason = {
    'AnomalyDetectionJudge': {'Baseline': 66.1, 'MCP Skills': 72.5, 'Native Skills': 71.3},
    'DiffPatternJudge': {'Baseline': 63.1, 'MCP Skills': 57.8, 'Native Skills': 61.6},
    'RCAJudge': {'Baseline': 70.9, 'MCP Skills': 71.3, 'Native Skills': 71.5},
}

gpt54_no_reason_sub = {
    'AnomalyDetectionUsage': {'Baseline': 56.8, 'MCP Skills': 71.8, 'Native Skills': 70.2},
    'TimeframeCorrectness': {'Baseline': 75.9, 'MCP Skills': 78.5, 'Native Skills': 77.9},
    'ToolCallsEfficiency': {'Baseline': 68.6, 'MCP Skills': 70.6, 'Native Skills': 69.1},
    'DedicatedToolsUsage': {'Baseline': 70.7, 'MCP Skills': 62.8, 'Native Skills': 70.1},
    'Methodology_DP': {'Baseline': 65.8, 'MCP Skills': 60.5, 'Native Skills': 63.5},
    'PatternCorrectness': {'Baseline': 55.4, 'MCP Skills': 52.8, 'Native Skills': 53.9},
}

gpt54_no_reason_latency = {'Baseline': 20.8, 'MCP Skills': 19.7, 'Native Skills': 22.5}

# === Section 6: gpt-5.1 reasoning ===
gpt51 = {
    'AnomalyDetectionJudge': {'Baseline': 57.7, 'MCP Skills': 62.8, 'Native Skills': 64.4},
    'DiffPatternJudge': {'Baseline': 59.9, 'MCP Skills': 61.6, 'Native Skills': 62.9},
    'RCAJudge': {'Baseline': 67.3, 'MCP Skills': 67.9, 'Native Skills': 68.3},
}

gpt51_latency = {'Baseline': 45.9, 'MCP Skills': 37.1, 'Native Skills': 44.1}

# === Section 7: gpt-5.4 + reasoning ===
gpt54_reason = {
    'AnomalyDetectionJudge': {'Baseline': 66.3, 'MCP Skills': 69.5, 'Native Skills': 69.4},
    'DiffPatternJudge': {'Baseline': 65.7, 'MCP Skills': 68.0, 'Native Skills': 67.3},
    'RCAJudge': {'Baseline': 69.4, 'MCP Skills': 71.5, 'Native Skills': 70.7},
}

gpt54_reason_latency = {'Baseline': 53.3, 'MCP Skills': 60.4, 'Native Skills': 56.1}

# === Section 10: Experiments A-E (gpt-5.4 + reasoning) ===
original = gpt54_reason

experiments = {
    'A: All Skills': {
        'AnomalyDetectionJudge': {'Baseline': 66.3, 'MCP Skills': 69.4, 'Native Skills': 67.0},
        'DiffPatternJudge': {'Baseline': 67.1, 'MCP Skills': 69.1, 'Native Skills': 65.4},
        'RCAJudge': {'Baseline': 70.8, 'MCP Skills': 71.0, 'Native Skills': 67.9},
    },
    'B: No Hints': {
        'AnomalyDetectionJudge': {'Baseline': 67.2, 'MCP Skills': 69.4, 'Native Skills': 65.7},
        'DiffPatternJudge': {'Baseline': 66.2, 'MCP Skills': 67.9, 'Native Skills': 64.4},
        'RCAJudge': {'Baseline': 69.8, 'MCP Skills': 71.2, 'Native Skills': 68.4},
    },
    'C: Concise': {
        'AnomalyDetectionJudge': {'Baseline': 66.3, 'MCP Skills': 69.2, 'Native Skills': 67.2},
        'DiffPatternJudge': {'Baseline': 67.0, 'MCP Skills': 66.4, 'Native Skills': 65.5},
        'RCAJudge': {'Baseline': 70.2, 'MCP Skills': 71.0, 'Native Skills': 68.6},
    },
    'E: Merged': {
        'AnomalyDetectionJudge': {'Baseline': 67.0, 'MCP Skills': 69.4, 'Native Skills': 68.0},
        'DiffPatternJudge': {'Baseline': 69.0, 'MCP Skills': 67.2, 'Native Skills': 66.8},
        'RCAJudge': {'Baseline': 71.8, 'MCP Skills': 70.3, 'Native Skills': 69.7},
    },
}

exp_latency = {
    'A: All Skills': {'Baseline': 295.5, 'MCP Skills': 286.9, 'Native Skills': 310.9},
    'B: No Hints': {'Baseline': 278.8, 'MCP Skills': 320.8, 'Native Skills': 340.3},
    'C: Concise': {'Baseline': 297.7, 'MCP Skills': 300.5, 'Native Skills': 323.0},
    'E: Merged': {'Baseline': 293.1, 'MCP Skills': 293.7, 'Native Skills': 322.1},
}


def _save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {path}")


# ======================================================================
# Section 2-3: gpt-5.4 no reasoning charts
# ======================================================================

def chart_s2_overall_accuracy():
    """Bar chart: 3 metrics x 3 flows for gpt-5.4 no reasoning."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(METRICS))
    width = 0.25
    for i, flow in enumerate(FLOWS):
        vals = [gpt54_no_reason[m][flow] for m in METRICS]
        bars = ax.bar(x + i * width, vals, width, label=flow, color=COLORS[flow], edgecolor='white')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.3,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_title('gpt-5.4 (No Reasoning) — Overall Accuracy', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels([METRIC_LABELS[m] for m in METRICS], fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(50, 80)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    _save(fig, 'chart_s2_overall.png')


def chart_s3_sub_metrics():
    """Grouped bar chart showing key sub-metrics for gpt-5.4 no reasoning."""
    sub_metrics = ['AnomalyDetectionUsage', 'DedicatedToolsUsage', 'TimeframeCorrectness',
                   'ToolCallsEfficiency', 'Methodology_DP', 'PatternCorrectness']
    labels = ['Anomaly\nUsage', 'DiffPatterns\nUsage', 'Timeframe\nCorrectness',
              'Tool Call\nEfficiency', 'Methodology\n(DP)', 'Pattern\nCorrectness']


    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = np.arange(len(sub_metrics))
    width = 0.25
    for i, flow in enumerate(FLOWS):
        vals = [gpt54_no_reason_sub[m][flow] for m in sub_metrics]
        bars = ax.bar(x + i * width, vals, width, label=flow, color=COLORS[flow], edgecolor='white')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.3,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=11)
    ax.set_title('gpt-5.4 (No Reasoning) — Sub-Metrics', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(fontsize=10)
    ax.set_ylim(45, 85)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    _save(fig, 'chart_s3_sub_metrics.png')


# ======================================================================
# Section 5 / Cross-model: All 3 model configs comparison
# ======================================================================

def chart_cross_model():
    """Compare all 3 model configs across 3 metrics — grouped by metric."""
    configs = {
        'gpt-5.4\n(no reasoning)': gpt54_no_reason,
        'gpt-5.1\n(reasoning)': gpt51,
        'gpt-5.4\n(+reasoning)': gpt54_reason,
    }
    config_names = list(configs.keys())

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharey=True)
    for idx, flow in enumerate(FLOWS):
        ax = axes[idx]
        x = np.arange(len(METRICS))
        width = 0.25
        for ci, (cname, cdata) in enumerate(configs.items()):
            vals = [cdata[m][flow] for m in METRICS]
            bars = ax.bar(x + ci * width, vals, width, label=cname if idx == 0 else '',
                          color=['#5B9BD5', '#FFC000', '#92D050'][ci], edgecolor='white')
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.3,
                        f'{val:.1f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
        ax.set_title(flow, fontsize=12, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels([METRIC_LABELS[m] for m in METRICS], fontsize=9)
        ax.set_ylim(50, 78)
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if idx == 0:
            ax.set_ylabel('Accuracy (%)', fontsize=11)

    fig.legend(config_names, loc='upper center', ncol=3, fontsize=10, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle('Cross-Model Comparison by Flow', fontsize=14, fontweight='bold', y=1.08)
    plt.tight_layout()
    _save(fig, 'chart_cross_model.png')


def chart_cross_model_latency():
    """Latency comparison across all 3 model configs."""
    configs = ['gpt-5.4\n(no reasoning)', 'gpt-5.1\n(reasoning)', 'gpt-5.4\n(+reasoning)']
    latencies = [gpt54_no_reason_latency, gpt51_latency, gpt54_reason_latency]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(configs))
    width = 0.25
    for i, flow in enumerate(FLOWS):
        vals = [lat[flow] for lat in latencies]
        bars = ax.bar(x + i * width, vals, width, label=flow, color=COLORS[flow], edgecolor='white')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.5,
                    f'{val:.1f}s', ha='center', va='bottom', fontsize=9)
    ax.set_ylabel('Avg Latency (seconds)', fontsize=12)
    ax.set_title('Latency by Model Configuration', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(configs, fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    _save(fig, 'chart_cross_model_latency.png')


def chart_diffpatterns_regression():
    """Show the DiffPatterns regression story: no-reasoning vs reasoning."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    configs = ['gpt-5.4\n(no reasoning)', 'gpt-5.1\n(reasoning)', 'gpt-5.4\n(+reasoning)']
    all_data = [gpt54_no_reason, gpt51, gpt54_reason]

    for flow in FLOWS:
        vals = [d['DiffPatternJudge'][flow] for d in all_data]
        ax.plot(configs, vals, marker='o', linewidth=2.5, markersize=10,
                label=flow, color=COLORS[flow])
        for xi, val in enumerate(vals):
            ax.annotate(f'{val:.1f}%', (xi, val), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=9, fontweight='bold')

    ax.set_ylabel('DiffPatterns Accuracy (%)', fontsize=12)
    ax.set_title('DiffPatterns Regression Story', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(52, 72)
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    _save(fig, 'chart_diffpatterns_story.png')


# ======================================================================
# Section 10: Experiment charts (unchanged from before)
# ======================================================================

def chart1_overall_rca_accuracy():
    fig, ax = plt.subplots(figsize=(10, 6))
    exp_names = ['Original\n(2 skills)'] + [k for k in experiments]
    x = np.arange(len(exp_names))
    width = 0.25
    for i, flow in enumerate(FLOWS):
        vals = [original['RCAJudge'][flow]]
        vals += [experiments[e]['RCAJudge'][flow] for e in experiments]
        bars = ax.bar(x + i * width, vals, width, label=flow, color=COLORS[flow], edgecolor='white')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.3,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_title('Overall RCA Accuracy by Experiment (gpt-5.4 + reasoning)', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(exp_names, fontsize=10)
    ax.legend(loc='lower right', fontsize=10)
    ax.set_ylim(60, 78)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    _save(fig, 'chart1_overall_rca.png')


def chart2_sub_metrics_heatmap():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    exp_names = ['Original'] + list(experiments.keys())
    for idx, metric in enumerate(METRICS):
        ax = axes[idx]
        data = []
        for flow in FLOWS:
            row = [original[metric][flow]]
            row += [experiments[e][metric][flow] for e in experiments]
            data.append(row)
        data_arr = np.array(data)
        im = ax.imshow(data_arr, cmap='RdYlGn', aspect='auto', vmin=60, vmax=75)
        ax.set_xticks(range(len(exp_names)))
        ax.set_xticklabels(exp_names, fontsize=8, rotation=30, ha='right')
        ax.set_yticks(range(len(FLOWS)))
        if idx == 0:
            ax.set_yticklabels(FLOWS, fontsize=10)
        ax.set_title(METRIC_LABELS[metric], fontsize=12, fontweight='bold')
        for i in range(len(FLOWS)):
            for j in range(len(exp_names)):
                ax.text(j, i, f'{data_arr[i, j]:.1f}', ha='center', va='center',
                        fontsize=9, fontweight='bold',
                        color='white' if data_arr[i, j] < 65 else 'black')
    fig.colorbar(im, ax=axes, shrink=0.8, label='Accuracy (%)')
    fig.suptitle('Experiment Sub-Metric Heatmap (gpt-5.4 + reasoning)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save(fig, 'chart2_heatmap.png')


def chart3_delta_vs_original():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for idx, metric in enumerate(METRICS):
        ax = axes[idx]
        exp_names = list(experiments.keys())
        x = np.arange(len(exp_names))
        width = 0.25
        for i, flow in enumerate(FLOWS):
            deltas = [experiments[e][metric][flow] - original[metric][flow] for e in experiments]
            bars = ax.bar(x + i * width, deltas, width, label=flow if idx == 0 else '',
                          color=COLORS[flow], edgecolor='white')
            for bar, val in zip(bars, deltas):
                ypos = bar.get_height() + 0.1 if val >= 0 else bar.get_height() - 0.4
                ax.text(bar.get_x() + bar.get_width() / 2., ypos,
                        f'{val:+.1f}', ha='center', va='bottom' if val >= 0 else 'top',
                        fontsize=7, fontweight='bold')
        ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8)
        ax.set_ylabel('Delta (pp)' if idx == 0 else '', fontsize=10)
        ax.set_title(METRIC_LABELS[metric], fontsize=11, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels(exp_names, fontsize=8, rotation=15, ha='right')
        ax.set_ylim(-6, 6)
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.legend(FLOWS, loc='upper center', ncol=3, fontsize=10, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle('Experiment Delta vs Original (Positive = Improvement)', fontsize=13, fontweight='bold', y=1.08)
    plt.tight_layout()
    _save(fig, 'chart3_deltas.png')


def chart4_latency_comparison():
    fig, ax = plt.subplots(figsize=(10, 6))
    exp_names = list(exp_latency.keys())
    x = np.arange(len(exp_names))
    width = 0.25
    for i, flow in enumerate(FLOWS):
        vals = [exp_latency[e][flow] for e in exp_names]
        bars = ax.bar(x + i * width, vals, width, label=flow, color=COLORS[flow], edgecolor='white')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 3,
                    f'{val:.0f}s', ha='center', va='bottom', fontsize=8)
    ax.set_ylabel('Avg Latency (seconds)', fontsize=12)
    ax.set_title('Experiment Latency (gpt-5.4 + reasoning)', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(exp_names, fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    _save(fig, 'chart4_latency.png')


def chart5_mcp_skills_wins():
    fig, ax = plt.subplots(figsize=(10, 6))
    exp_names = ['Original'] + list(experiments.keys())
    for metric in METRICS:
        vals = [original[metric]['MCP Skills']]
        vals += [experiments[e][metric]['MCP Skills'] for e in experiments]
        ax.plot(exp_names, vals, marker='o', linewidth=2.5, markersize=8,
                label=METRIC_LABELS[metric])
    ax.set_ylabel('MCP Skills Accuracy (%)', fontsize=12)
    ax.set_title('MCP Skills Accuracy Across Experiments', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(62, 76)
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    _save(fig, 'chart5_mcp_skills_trend.png')


if __name__ == '__main__':
    # Section 2-3: gpt-5.4 no reasoning
    chart_s2_overall_accuracy()
    chart_s3_sub_metrics()

    # Cross-model comparison (sections 6-7)
    chart_cross_model()
    chart_cross_model_latency()
    chart_diffpatterns_regression()

    # Section 10: Experiments
    chart1_overall_rca_accuracy()
    chart2_sub_metrics_heatmap()
    chart3_delta_vs_original()
    chart4_latency_comparison()
    chart5_mcp_skills_wins()

    print("All charts generated!")
