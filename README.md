# CP-SAN: Context-Aware Parameter Sanitization for MCP Tool Calls

CP-SAN is a defense system that sits at the host orchestration layer of Model Context Protocol (MCP) agent pipelines. It inspects tool call parameters before they're executed, using a two-layer approach — fast pattern matching followed by an LLM-based semantic check — to catch prompt injection and parameter manipulation attacks that pattern matching alone would miss.

## How it works

1. **Pattern layer** — regex/heuristic checks flag obviously suspicious parameter values (`sanitizer/classifier.py`).
2. **Semantic layer** — Gemini 2.5 Flash reviews flagged (and borderline) tool calls in context, deciding whether the parameters are consistent with the user's actual task, and rewrites or blocks unsafe ones (`sanitizer/rewriter.py`).
3. Both layers are combined in `sanitizer/sanitizer.py`, which is the main entry point used by the evaluation scripts.

## Repository structure

```
sanitizer/       Core CP-SAN implementation (classifier, rewriter, orchestration)
tools/           MCP tool registry used in evaluation scenarios
attacks/         Attack scenario generation and the final scenario datasets
evaluation/      Scripts to run each experiment configuration and score results
results/         Output logs and summaries from evaluation runs
InjecAgent/      Submodule / external benchmark used for cross-comparison
```

## Evaluation

The system is evaluated on a dataset of 200 adversarial tool-call scenarios across 8 attack categories (Exfiltration, Lateral Movement, Persistence, Privilege Escalation, Semantic Deception, Multi-Parameter Attack, Evasion Attack, Context Manipulation), plus 100 legitimate scenarios used to measure false positives and task completion.

Run configurations from `evaluation/`:

| Script | Configuration |
|---|---|
| `run_nodefense.py` | No defense (baseline) |
| `run_pattern_only.py` | Pattern layer only |
| `run_llm_only.py` | Semantic (LLM) layer only |
| `run_cpsan_full.py` | Full CP-SAN (pattern + semantic) |
| `run_llamaguard.py` | Llama Guard 3 8B as an independent safety-judge baseline |

### Ablation results (Attack Success Rate)

| Configuration | ASR |
|---|---|
| No Defense | 100% |
| Pattern Only | 54.2% |
| LLM Only | 21.4% |
| **CP-SAN Full** | **13.4%** |

### Comparison to an existing safety classifier

| System | ASR |
|---|---|
| Llama Guard 3 8B (generic baseline) | 64.7% |
| **CP-SAN Full** | **13.4%** |

CP-SAN Full also achieves a 99% task completion rate (TCR) and a 1% false positive rate (FPR) on the legitimate-scenario set, indicating the defense doesn't meaningfully interfere with normal tool use.

## Setup

```bash
pip install -r requirements.txt   # or install groq, google-generativeai, openai, python-dotenv individually
```

Create a `.env` file in the project root with your API keys:

```
GROQ_API_KEY=your_groq_key
```
The Llama Guard baseline runs locally via [Ollama](https://ollama.com) rather than a hosted API (Groq deprecated their hosted `llama-guard-3-8b` endpoint). Pull the model first:

```bash
ollama pull llama-guard3:8b
```

## Running an evaluation

```bash
python evaluation/run_cpsan_full.py
python evaluation/run_llamaguard.py
```

Results are written to `results/` as CSV/JSON logs, with per-category and overall ASR summaries printed to console.

## Notes

- Attack scenarios were generated and reviewed under `attacks/`, with an additional cross-check against the InjecAgent benchmark (`attacks/load_injecagent.py`, `attacks/injecagent_scenarios.json`).
- This repository accompanies an ongoing research submission; results and structure may change as the writeup is finalized.
