# FOLIO: Retrieval-Augmented Logical Reasoning and First-Order Logic Translation

**A course research project exploring retrieval-augmented language models and neuro-symbolic reasoning on the FOLIO benchmark.**

[![Python](https://img.shields.io/badge/Python-3.11%20(tested%20environment)-3776AB?logo=python&logoColor=white)](#getting-started) [![Dataset](https://img.shields.io/badge/Benchmark-FOLIO-blue)](#benchmark-and-evaluation) [![Methods](https://img.shields.io/badge/Methods-SeRAG%20%7C%20ST--RAG-informational)](#approaches)

> **Academic context:** The course *Language Models and Structured Data* (APM_5AI29_TP), Télécom Paris / Institut Polytechnique de Paris. Team: **VNAI (Vietnamese AI Team)**. This repository accompanies the course project report, *Reasoning and Translating to First-Order Logic using Large Language Models on FOLIO*.

## Overview

Large language models can generate plausible natural-language answers without guaranteeing logically valid inferences or well-formed formal expressions. This project investigates two related tasks on [FOLIO](https://huggingface.co/datasets/yale-nlp/FOLIO):

1. **Logical entailment classification:** given natural-language premises and a hypothesis, predict **True**, **False**, or **Uncertain**.
2. **Natural-language-to-first-order-logic (NL→FOL) translation:** formalize premises and conclusions into FOL expressions that can be checked with a symbolic solver.

The project studies **retrieved in-context examples**, **step-by-step translation demonstrations**, and an **LLM-assisted error-correction loop**, with an emphasis on the trade-off between classification accuracy, FOL syntax validity, and runtime.

## Key results

The following numbers are **reported in the accompanying course report**.

| Logical reasoning method | Model | Accuracy ↑ | Reported runtime (s) ↓ |
| --- | --- | ---: | ---: |
| Direct LLM | Qwen2.5 3B | 36.27% | 3.13 |
| Direct LLM | Qwen2.5 14B | 52.94% | 25.48 |
| Logic-of-Thought (LoT) | Qwen2.5 14B | 58.30% | 26.47 |
| **SeRAG** | **Qwen2.5 14B** | **63.73%** | 57.22 |
| **ST-RAG** | **Qwen2.5 14B** | **64.22%** | 80.06 |

On the same reported setup, **ST-RAG improves reasoning accuracy by 11.28 percentage points over direct Qwen2.5 14B prompting**, at a higher inference cost.

| NL→FOL translation method | Model | Syntax validity ↑ | Execution accuracy ↑ |
| --- | --- | ---: | ---: |
| Direct LLM translation | Qwen2.5 3B | 59.31% | 42.17% |
| Direct LLM translation | Qwen2.5 14B | 71.08% | 62.07% |
| Step-by-step translation without RAG (ST-noRAG) | Qwen2.5 14B | 83.33% | 65.29% |
| ST-RAG without fixer | Qwen2.5 14B | 78.92% | **68.94%** |
| **Full ST-RAG** | **Qwen2.5 14B** | **93.13%** | 66.32% |

The full ST-RAG method achieves the highest **syntax validity** in this comparison, but **not** the highest execution accuracy. The distinction matters: a formula may parse successfully yet fail to preserve the intended meaning.

## Approaches

### 1. SeRAG — Semantic Retrieval-Augmented Generation

SeRAG extends few-shot logical reasoning by selecting examples dynamically instead of relying exclusively on a fixed prompt.

```text
Natural-language premises + conclusion
                   │
                   ▼
           Text embedding
                   │
                   ▼
      Retrieve similar examples
       (FAISS nearest neighbors)
                   │
                   ▼
     Few-shot prompt + input query
                   │
                   ▼
               LLM
                   │
                   ▼
        True / False / Uncertain
```

The repository uses the **BAAI/bge-small-en-v1.5** embedding model through `fastembed`; the SeRAG retriever builds a **FAISS `IndexFlatL2`** over example embeddings. Retrieved premises, conclusions, and labels are inserted into the LLM prompt.

**Implementation:** `agent/ltrag/rag_predictor.py`, `agent/ltrag/retrieval/retriever.py`.

### 2. ST-RAG — Step-by-Step Translation with Retrieval

ST-RAG targets formalization: producing FOL expressions suitable for symbolic reasoning. Its retrieved examples contain natural-language sentences, predicate and constant information, translation steps, and reference FOL formulas.

```text
Natural-language problem
          │
          ├─────────────► Retrieve relevant translation examples
          │                (semantic/story-level similarity)
          │                              │
          └──────────────────────────────┤
                                         ▼
                             Translation LLM
                              (structured FOL)
                                         │
                                         ▼
                              FOL parser + Z3
                                         │
                         ┌───────────────┴──────────────┐
                         │                              │
                      Valid                       Parsing error
                         │                              │
                         ▼                              ▼
                  Entailment check              LLM-based fixer
                         │                              │
                         ▼                              └── Retry (bounded)
              True / False / Uncertain
```

The source contains several translation pipelines and ablations, including story-level retrieval, translation without the retrieval/fixer combination, and fixer-based prediction. **The exact behavior depends on the entry-point script chosen.** In particular, the currently active `RagFixer` implementation supplies a small set of error rules to the LLM rather than retrieving error examples; an alternative retrieval-based implementation is present but commented out.

**Implementation:** `agent/ltrag/translation/`, `agent/ltrag/retrieval/`, `agent/ltrag/fixer/`, `agent/ltrag/translate_story_fix_predictor.py`.

### Symbolic reasoning with Z3

The repository includes a FOL processing pipeline that:

1. Tokenizes and parses generated formulas into an intermediate abstract syntax tree.
2. Encodes parsed formulas as Z3 expressions.
3. Checks whether the premises entail the conclusion, its negation, or neither.

This provides the three-way **True / False / Uncertain** output. The solver can verify entailment for the *generated formalization*; it cannot independently guarantee that the generated FOL matches the original natural-language meaning.

**Implementation:** `z3_module/fol_lexer.py`, `fol_parser.py`, `ast_fol.py`, `z3_encoder.py`, `reasoner.py`.

## Benchmark and evaluation

The [FOLIO benchmark](https://huggingface.co/datasets/yale-nlp/FOLIO) contains natural-language premises and conclusions with FOL annotations and three-way entailment labels. The report describes **1,435 labeled examples across 487 stories**.

Metrics used in the report:

- **Reasoning accuracy:** proportion of correctly predicted entailment labels.
- **Syntax validity (SynV):** proportion of generated FOL expressions that are syntactically valid.
- **Execution accuracy (ExcAcc):** proportion of examples for which the generated formalization produces the correct entailment outcome when executed by the solver.
- **Runtime:** reported elapsed time in seconds for the evaluated methods (see the report for experimental context).

## Repository structure

```text
FOLIO/
├── agent/
│   ├── base_predictor.py          # Shared predictor interface
│   ├── naive_predictor/          # Direct LLM baselines
│   └── ltrag/
│       ├── retrieval/             # Example and story retrieval
│       ├── translation/           # NL-to-FOL translation prompts
│       ├── fixer/                 # FOL correction strategies
│       ├── solver/                # Solver-related scripts
│       └── *_predictor.py         # RAG, translation and fixer variants
├── config/config.py              # Model, endpoint, and retrieval settings
├── data/                         # FOLIO JSONL splits and cached KB data
├── kb/                           # Translation and fixer knowledge bases
├── llm/
│   ├── llm_client.py              # OpenAI-compatible chat client
│   └── local_embedder.py          # Local sentence embeddings
├── run/                           # Experiment entry points and utilities
├── results/                       # Saved experiment outputs and dependency list
└── z3_module/                     # FOL parser, encoder, and Z3 reasoner
```

## Getting started

### Prerequisites

- Python (the supplied archive includes Python 3.11 bytecode artifacts; **3.11 is a sensible starting point**, not a verified compatibility guarantee).
- [Ollama](https://ollama.com/) for the default local LLM configuration.
- Disk space for the chosen local model and embedding model.

Run the following commands **from the `FOLIO/` repository root**, so local imports and relative data paths resolve correctly:

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r ./requirements.txt
```

### Configure the language model

The default `config/config.py` specifies an Ollama OpenAI-compatible endpoint and `qwen2.5:3b`. To use it:

```bash
ollama pull qwen2.5:3b
ollama serve
```

Keep the Ollama server running in another terminal. To use the larger model from the reported experiments, run `ollama pull qwen2.5:14b` and change `LLM_MODEL` in `config/config.py` accordingly. The LLM wrapper also has provider branches for Groq and DeepSeek, but alternative provider credentials and endpoints must be configured separately.

### Run an experiment

From the repository root:

```bash
# Direct reasoning baseline
python -m run.run_naive_predictor

# SeRAG: retrieved few-shot logical reasoning
python -m run.run_rag_predictor

# Natural-language to FOL translation + retrieval
python -m run.run_translate_rag_predictor

# Story-level translation with a fixer and symbolic solver
python -m run.run_translate_story_fix
```

Additional entry points can be found under `run/`. The common runner in `run/util.py` reads `data/folio-validation.jsonl`, **uses up to 204 samples by default**, prints the prediction and ground truth per sample, and reports accuracy. Change the runner arguments in the scripts or `run/util.py` to adjust the dataset path or number of examples.

**Reproducibility note:** These are source-verified entry points, not end-to-end commands validated in this environment. Model availability, dependencies, cached embeddings, and local configuration affect execution. The supplied repository snapshot does not include a single automated reproduction command for every table in the report.

## Limitations and future work

The report identifies several open challenges:

- **Example selection:** manually curated or tuned knowledge bases may limit scalability and generalization.
- **Formalization robustness:** predicate-arity mismatches and complex, inconsistent formulas remain difficult to correct.
- **Semantic fidelity:** syntax validity and execution accuracy alone do not fully capture NL↔FOL meaning preservation.
- **Cost:** retrieved prompting and iterative correction increase inference time.

Potential next steps include expanding knowledge bases automatically, improving cross-premise consistency and error repair, exploring parameter-efficient fine-tuning (e.g., LoRA), and designing more informative translation metrics.

## References

This project draws on established work rather than claiming to introduce retrieval-based formalization from scratch:

1. **FOLIO:** Han et al., *FOLIO: Natural Language Reasoning with First-Order Logic*, EMNLP 2024.
2. **LTRAG:** Hu et al., *LTRAG: Enhancing Autoformalization and Self-Refinement for Logical Reasoning with Thought-Guided RAG*, Findings of ACL 2025.
3. **Logic-of-Thought:** Liu et al., *Logic-of-Thought: Injecting Logic into Contexts for Full Reasoning in Large Language Models*, NAACL 2025.
4. **LINC:** Olausson et al., *LINC: A Neurosymbolic Approach for Logical Reasoning by Combining Language Models with First-Order Logic Provers*, EMNLP 2023.
5. **Logic-LM:** Pan et al., *Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning*, Findings of EMNLP 2023.

For the full methodology, experimental results, and error analysis, see the accompanying **VNAI course project report** (if published alongside this repository).

## Project status

**Academic research prototype.** This repository contains experimental implementations and saved outputs. It is not presented as a production-ready logical reasoning service, and the reported benchmark figures should be understood as results from the course report rather than a guarantee for every commit or execution environment.
