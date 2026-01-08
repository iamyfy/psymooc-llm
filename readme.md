# Patient Agent

**A Multi-agent LLM System for Psychiatric Patient Simulation**

## Overview

Patient Agent is a backend system for simulating psychiatric patients supporting multi-turn clinical interviews, controlled patient behavior, and automated generation of structured psychiatric case records and feedbacks.

The system is intended for **psychiatric education, simulation-based training, and human–AI interaction research**, rather than clinical deployment.

---
## Note
In addition to the backend system released in this repository, the project includes a Unity-based frontend used for interactive interviews. This project is under active development. The current version represents a stable research prototype used in the reported experiments. Ongoing updates will be done without changing the core system design described in this submission.

---

## Research Contribution

The system demonstrates:

1. **LLM-based patient simulation** grounded in psychiatric knowledge via RAG
2. **Behaviorally controlled dialogue** (e.g., trust, cooperativeness, affective response)
3. **End-to-end interview pipelines**, from dialogue to structured clinical documentation
4. **Programmatic evaluation** of clinician–patient interactions through automated scoring and feedback agents

---

## System Design

### Architecture

* **LLM Backbone**: OpenAI-compatible large language models
* **RAG Pipeline**: LangGraph-orchestrated retrieval and generation over psychiatric knowledge
* **Knowledge Base**: DSM-related and clinical reference documents indexed with FAISS
* **Dialogue Policy**: Explicit dialogue state and behavioral policy control
* **API Layer**: RESTful interface for reproducible experiments

---

## Core Functionalities

* **Patient Generation**
  Patients are instantiated from demographic and diagnostic parameters (e.g., age, diagnosis, severity).

* **Multi-Turn Interview Simulation**
  Supports longitudinal, stateful clinical conversations.

* **Behavioral Modeling**
  Patient responses vary along clinically relevant dimensions (e.g., engagement, emotional reactivity).

* **Clinical Record Synthesis**
  Automatically produces structured psychiatric records from simulated interviews.

* **Interaction Evaluation**
  Generates multi-dimension scores and qualitative feedback for interview performance analysis.

---

## Reproducibility

### Requirements

* Python ≥ 3.9
* OpenAI-compatible API key

### Installation

```bash
pip install -r requirements.txt
```

### Execution

```bash
python app.py
```

The system exposes a REST API at `http://localhost:5000`.

---

## Ethical Use Statement
This system **does not provide medical diagnosis or treatment**.
All patient interactions are synthetic and intended solely for **research and educational purposes**.

---

## License

MIT License.

---
