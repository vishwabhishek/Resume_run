Project: Smart Shortlist — Candidate Shortlisting for Recruiters

Overview
--------
This project produces trustworthy shortlists of candidates for a given job description by combining semantic understanding of the JD, candidate career history, skills, behavioral signals, and platform activity. The goal is not to merely extract keywords, but to reason about fit and surface a concise, recruitable shortlist.

What your solution needs to do
--------------------------------
- Read a job description and actually understand what the role needs — not just pull out words.
- Look at the full picture — career history, skills, behavioral signals, platform activity — and figure out who genuinely fits.
- Deliver a shortlist that a recruiter can trust.

How to build it (open-ended)
----------------------------
You can use any combination of methods: semantic search, LLM ranking, vector embeddings, hybrid scoring, or other architectures. The outcome (quality of the shortlist) is what matters. The repository provides a starting point and example scripts; adapt components as you like.

What I built (suggested implementation)
--------------------------------------
- Data ingestion: normalize candidate records and job descriptions into a common text representation.
- Embeddings & semantic retrieval: convert JD + candidate profiles into vector embeddings (any embedding provider or open-source model). Use semantic search to get an initial candidate set.
- Feature scoring: compute structured signals — skill overlap, tenure, role seniority match, recency of activity, behavioral indicators (e.g., public contributions), and custom heuristics.
- LLM ranking & calibration: use an LLM to rank the semantic shortlist, providing explanations and a confidence score; optionally re-rank using a small cross-encoder model for accuracy.
- Hybrid final score: combine embedding-similarity, feature scores, and LLM ranker outputs into a final score and select the top-N candidates.

Repository structure and important files
--------------------------------------
- dashboard.html — simple visual dashboard for results.
- rank.py — example ranking pipeline (entry point to build on).
- requirements.txt — Python dependencies to install.
- submission.csv / submission_metadata.yaml — sample submission artifacts.
- scratch/ — collection of utility scripts and analysis helpers (data cleaning, diagnostics, PDF export, dashboard generation).

How it works (end-to-end)
-------------------------
1. Preprocess: normalize candidates in JSONL or CSV form, extract canonical fields (roles, dates, skills, summaries).
2. Embed: create vector embeddings for job description and candidate textual profiles.
3. Retrieve: perform nearest-neighbor search to get an initial candidate pool.
4. Score: compute structured feature scores and pass the pool to an LLM ranker for fine-grained ordering and explanations.
5. Combine: fuse semantic, feature, and LLM scores into a hybrid score.
6. Output: produce a ranked shortlist CSV/JSON with explanation and confidence for each candidate.

Example: quick local run
------------------------
1. Create a Python environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Prepare data: ensure your candidate JSONL/CSV is available. The repo contains sample files under extracted_data/.

3. Run the sample ranking pipeline (example):

```bash
python rank.py --job description.txt --candidates extracted_data/India_runs_data_and_ai_challenge/candidates.jsonl --output shortlist.csv
```

Notes: rank.py is a starting example. Implement or swap embedding, retrieval, and ranking components as needed.

Evaluation & deliverable
------------------------
- Deliverable: a short report (this README or a separate document) explaining the approach, the ranking pipeline, and how to reproduce results.
- Evaluations: measure precision@k, recall (if ground truth exists), qualitative inspection of LLM explanations, and recruiter feedback loops.

Design choices and rationale
---------------------------
- Use semantic embeddings to capture intent beyond keywords.
- Add structured feature scoring to encode domain knowledge (seniority mapping, skill synonyms, career gaps).
- Use LLMs for nuanced ranking and human-readable explanations to increase recruiter trust.
- Hybrid scoring reduces single-model failure modes and gives a tunable tradeoff between precision and recall.

Extending the project
----------------------
- Replace embedding model/provider for better on-prem or privacy-preserving solutions.
- Train or fine-tune a small cross-encoder on curated pairwise labels for higher ranking accuracy.
- Add active learning: collect recruiter feedback to fine-tune weightings or label data for supervised learning.

Privacy & ethics
----------------
Be careful with PII and sensitive attributes. Respect anti-discrimination laws and avoid using protected characteristics as ranking signals. Log and audit model decisions when used in hiring-critical contexts.

Contact / Next steps
--------------------
If you want, I can:
- Run the example pipeline on the repository data and produce a sample shortlist.csv.
- Implement a simple embedding + retrieval demo integrated into rank.py.
- Add a short report.md describing experiments and results.

-- End of README

Detailed approach & architecture
-------------------------------
This section describes a concrete, reproducible architecture you can implement as a baseline. It's intentionally modular so you can replace components.

Components
- Ingest & Normalizer: parse candidate JSONL/CSV and job descriptions, normalize dates/role titles, expand skill synonyms, produce a profile string per candidate.
- Embedding store: compute vector embeddings for each candidate profile and the job description. Options: OpenAI embeddings, Cohere, Hugging Face sentence-transformers. Store vectors in FAISS or an in-memory index.
- Retriever: nearest-neighbor search (FAISS/Annoy) to get top-K candidates by cosine similarity.
- Feature extractor: compute numeric signals for each candidate: skill_overlap, seniority_match, avg_tenure, recency_score, activity_score, education_match, geographic_preference (if applicable).
- LLM ranker (optional but recommended): feed the top-K with context to an LLM to request ranked list + short rationale and a confidence score. Alternatively use a cross-encoder (pairwise scoring) for better accuracy.
- Scoring & fusion: combine embedding similarity, normalized feature scores, and LLM ranking into a final scalar score. Example fusion formula: final = w1*sim + w2*features + w3*llm_score (tune w1..w3 on validation data).
- Output & explainability: export the top-N with per-candidate explanations and a JSON/CSV for recruiters and a visual dashboard.

Suggested baseline stack
- Python 3.10+
- Libraries: sentence-transformers, faiss-cpu, numpy, pandas, scikit-learn, openai (optional), transformers (optional), tqdm
- Persistence: store candidate vectors in FAISS and metadata in JSONL or a light DB (SQLite)

Scoring example (illustrative)
- skill_overlap = (#matching_skills / #required_skills)
- seniority_score = 1 - abs(level_map(candidate_title) - level_map(jd_title)) / max_level
- recency_score = sigmoid(days_since_last_role / 365)
- features = 0.5*skill_overlap + 0.3*seniority_score + 0.2*recency_score
- final_score = normalize(similarity) * 0.6 + normalize(features) * 0.3 + normalize(llm_score) * 0.1

Run & evaluation instructions (detailed)
---------------------------------------
1) Setup environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Prepare data
- Place your candidate dataset in JSONL or CSV. The repository contains sample data under `extracted_data/`.

3) Baseline run (embedding + retrieval)

```bash
# produce embeddings and index
python rank.py --build-index --candidates extracted_data/India_runs_data_and_ai_challenge/candidates.jsonl --index-path data/faiss.index

# retrieve and score for a JD
python rank.py --job job_description.txt --index-path data/faiss.index --topk 200 --output shortlist_raw.csv
```

4) LLM re-ranking (optional)

```bash
python rank.py --job job_description.txt --index-path data/faiss.index --topk 200 --llm-rerank --output shortlist_final.csv
```

5) Evaluation
- If you have labels/ground truth, compute precision@k and recall for top-K:

```python
from sklearn.metrics import precision_score
# or implement precision_at_k utility
```
- Manually review LLM rationales for a small sample and collect recruiter feedback.

Usage examples
--------------
- Quick local example (assumes sample data present):

```bash
python rank.py --job scratch/job_description.txt --candidates extracted_data/India_runs_data_and_ai_challenge/candidates.jsonl --output results/shortlist.csv
```

- Inspect results: open `dashboard.html` in a browser or view the CSV.

Files in this repository (summary)
---------------------------------
- `dashboard.html` — interactive visualization of shortlisted candidates and scores.
- `rank.py` — core script: index building, retrieval, and optional LLM re-ranking. (Entrypoint for experiments.)
- `requirements.txt` — pip dependencies.
- `submission.csv`, `submission_metadata.yaml` — example output/metadata formats.
- `extracted_data/` — sample data and helper files used in this challenge.
- `scratch/` — utilities: data cleaning, diagnostics, PDF export, and helper scripts.

Next steps & extension ideas
---------------------------
- Implement end-to-end demo: small script in `scratch/` that builds index, runs retrieval, and re-ranks with a free embedding model.
- Add unit tests for normalization and scoring logic.
- Build a lightweight web UI (Flask/Streamlit) for recruiters to tweak weights and provide feedback.
- Implement active learning: capture recruiter clicks/accepts and use them to fine-tune ranking or weights.

Reproducibility notes
---------------------
- Include seeds for random components when evaluating.
- Version control model/configuration choices; keep a `config.yaml` to record model names and weights.

If you'd like, I will now mark the remaining TODOS complete and can implement the baseline demo in `rank.py`.
