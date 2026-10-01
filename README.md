# CP-SAN: Context-Aware Parameter Sanitization for MCP Tool Calls

CP-SAN is a defense system that sits at the host orchestration layer of Model Context Protocol (MCP) agent pipelines. It inspects tool call parameters before they're executed, using a layered approach — pattern matching, an LLM-based tool-context check, and LLM-based scope/rewrite evaluation — to catch prompt injection and parameter manipulation attacks that pattern matching alone would miss.

## How it works

1. **Tool-context check** — an LLM evaluates whether the requested tool is reasonable for the user's stated task at all (`sanitizer/sanitizer.py`).
2. **Pattern layer** — per-parameter substring denylist checks flag suspicious parameter values (`tools/tool_registry.py`, applied in `sanitizer/sanitizer.py`).
3. **Scope layer** — an LLM (`sanitizer/classifier.py`) evaluates whether each parameter value is consistent with its declared scope and the user's task.
4. If a parameter is flagged by either the pattern or scope check, `sanitizer/rewriter.py` attempts to rewrite it to a safe equivalent; if no safe rewrite is possible, a safe default is used.

The semantic layers (tool-context check, scope check, rewrite) run on Groq (`openai/gpt-oss-120b` as of the current implementation).

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
| `run_llm_only.py` | Scope layer only |
| `run_cpsan_full.py` | Full CP-SAN (tool-context + pattern + scope + rewrite) |
| `run_llamaguard.py` | Llama Guard 3 8B as an independent safety-judge baseline |

### Ablation results (Attack Success Rate)

| Configuration | ASR |
|---|---|
| No Defense | 100.0% |
| Pattern Only | 54.2% |
| LLM Only (scope check) | 27.4% |
| **CP-SAN Full** | **18.4%** |

### Comparison to an existing safety classifier

| System | ASR |
|---|---|
| Llama Guard 3 8B (generic baseline) | 64.7% |
| **CP-SAN Full** | **18.4%** |

CP-SAN Full achieves a 93.0% task completion rate (TCR) and a 7.0% false positive rate (FPR) on the legitimate-scenario set. False positives mostly arise from the tool-context check being conservative about unconventional-but-legitimate tool usage (e.g., using `execute_command` to run a formatter, or `write_file` for creative writing).

## Setup

```bash
pip install -r requirements.txt   # or install groq, openai, python-dotenv individually
```

Create a `.env` file in the project root with your API key(s):

```
GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-120b
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
- CP-SAN's semantic layers depend on a hosted LLM (Groq). The model used has already changed twice during this project's development (Llama 3.3 70B → GPT-OSS 120B) due to provider-side model deprecations — a dependency risk discussed in the accompanying paper.
- This repository accompanies an ongoing research submission; results and structure may change as the writeup is finalized.
