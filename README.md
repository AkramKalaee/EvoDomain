# EvoDomain

**Search-based domain-oriented test suite generation for logic-based testing**

EvoDomain is a search-based approach for enhancing logic-based testing with **domain-oriented test generation**. It addresses a limitation of conventional logic-based criteria such as **Modified Condition/Decision Coverage (MC/DC)**: satisfying logic-based coverage does not necessarily ensure adequate exploration of the boundaries between feasible input domains.

EvoDomain searches for boundary-oriented test data and uses it to augment an MC/DC-adequate test suite, improving its ability to detect **domain errors** caused by incorrect or shifted decision boundaries.

<p align="center">
  <a href="https://doi.org/10.1016/j.infsof.2024.107564">
    <img src="https://img.shields.io/badge/Paper-Information%20and%20Software%20Technology-blue" alt="Published paper">
  </a>
  <a href="https://doi.org/10.1016/j.infsof.2024.107564">
    <img src="https://img.shields.io/badge/DOI-10.1016%2Fj.infsof.2024.107564-green" alt="DOI">
  </a>
</p>

---

## 🔍 Overview

A program can be viewed as mapping its input space into a finite set of **feasible domains**, each associated with particular execution behavior.

Traditional logic-based testing focuses on exercising logical conditions and decisions. EvoDomain complements this perspective by explicitly exploring the **boundaries of feasible input domains**, where domain-related faults may cause a program to follow an incorrect execution path.

The resulting test suite combines:

```text
MC/DC
   │
   ├── Logical condition/decision coverage
   │
   └── EvoDomain
          │
          └── Domain-boundary exploration
                    │
                    ▼
          Enhanced test suite
                    │
                    ▼
          Improved domain-error detection
```

## 💡 Why EvoDomain?

Logic-based coverage criteria such as MC/DC are effective at demonstrating the independent effect of conditions on decisions. However, a test suite can satisfy MC/DC while still providing insufficient coverage of the **input-space regions defined by those decisions**.

This becomes particularly important when faults involve arithmetic expressions that **shift or tilt domain boundaries**.

EvoDomain therefore addresses a complementary testing question:

> **How can we generate diverse test data around the boundaries of feasible input domains?**

## 🧬 Approach

EvoDomain dynamically generates domain-oriented test data using a **memetic search strategy** that combines genetic search with local search.

The approach consists of four main ideas:

* **Domain identification** — identify feasible subdomains associated with testing requirements.
* **Memetic search** — combine genetic algorithms with hill-climbing to efficiently explore the search space.
* **Boundary test generation** — search for test data around feasible-domain boundaries.
* **Diversity selection** — use **DBSCAN clustering** to select diverse boundary-oriented test data.

The selected test data are then used to augment an **MC/DC-adequate test suite**, extending its ability to expose domain-specific faults.

### Architecture

<p align="center">
  <img src="docs/images/diagram.png" alt="EvoDomain architecture" width="750">
</p>

## 🧭 Boundary-Oriented Test Generation

The following examples illustrate the evolution of domain-oriented test generation across the input space.

<p align="center">
  <img src="docs/images/ex1.gif" alt="Domain generation example 1" width="600">
</p>

<p align="center">
  <img src="docs/images/ex2.gif" alt="Domain generation example 2" width="600">
</p>

These visualizations show how the search explores feasible regions and identifies representative test data around their boundaries.

## 🧪 Experimental Evaluation

EvoDomain was evaluated on **30 case studies**, including **11 classic problems and 19 cases from an industrial problem**. The evaluation compares EvoDomain with logic-based testing approaches, domain-oriented test generation, and Random Search.

### Key Findings

The reported results show that EvoDomain:

* Increased fault detection by **74.44% compared with MC/DC** and **65.06% compared with RoRG**.
* Improved support for different fault types by up to **68.89% for MC/DC** and **66.33% for RoRG**.
* Improved convergence effectiveness for identifying feasible subdomains by **32% compared with COSMOS**.
* Achieved **0.99–1.00 accuracy and F1-score** for domain identification.
* Identified feasible subdomains in **less than one-third of the time required by Random Search**.
* Also improved the effectiveness of spectrum-based fault localization, with reported improvements of up to **53.16% for Ochiai, 47.97% for Tarantula, and 51.68% for Jaccard**.

## 📁 Repository Structure

```text
EvoDomain/
│
├── docs/
│   └── images/
│       ├── diagram.png
│       ├── ex1.gif
│       └── ex2.gif
│
├── experiments/
│   ├── CFG/
│   ├── Code/
│   ├── Domain/
│   └── path/
│
├── src/
│   ├── cfg/
│   ├── code_coverage/
│   ├── domain/
│   │   ├── mcmc/
│   │   └── multi_swarm/
│   ├── GA/
│   ├── instrument/
│   └── sut/
│
├── Evaluation measurements.ipynb
├── Postprocessing.ipynb
├── requirements.txt
└── README.md
```

### Main Components

| Component                 | Purpose                                      |
| ------------------------- | -------------------------------------------- |
| `src/GA/`                 | Genetic and local search components          |
| `src/domain/`             | Domain and boundary analysis                 |
| `src/domain/mcmc/`        | MCMC-based domain exploration                |
| `src/domain/multi_swarm/` | Multi-swarm search and local exploration     |
| `src/instrument/`         | Program instrumentation                      |
| `src/cfg/`                | Control-flow graph analysis                  |
| `src/code_coverage/`      | Path and coverage analysis                   |
| `src/sut/`                | Programs used as systems under test          |
| `experiments/`            | Experimental artifacts and generated results |

## ⚙️ Installation

EvoDomain was originally developed and evaluated using:

**Python 3.6.4**

Install the required packages with:

```bash
pip install -r requirements.txt
```

The current `requirements.txt` lists the required packages without version pins because the exact dependency versions from the original experimental environment are no longer available.

## ▶️ Usage

The main entry point is:

```bash
python src/main.py
```

Individual components under `src/` can also be used for specific experiments and analyses.

## 📊 Evaluation Notebooks

### Evaluation Measurements

[`Evaluation measurements.ipynb`](Evaluation%20measurements.ipynb)

Contains the scripts and analyses used to evaluate the generated domain-oriented test suites.

### DBSCAN Postprocessing

[`Postprocessing.ipynb`](Postprocessing.ipynb)

Contains the clustering and postprocessing procedures used to select diverse boundary-oriented test data.

## 🔬 Research Contribution

EvoDomain extends logic-based testing by introducing **domain-oriented test generation** into the test-suite construction process.

Its central idea is to complement logical coverage with explicit exploration of **feasible-domain boundaries**, providing additional test data that can expose domain errors that may remain undetected by conventional logic-based coverage alone.

This work established the basis for subsequent research on **behavioral-domain testing**, extending the idea of domain-oriented adequacy toward increasingly complex software-intensive systems.

## 📖 Publication

**Kalaee, A., Parsa, S., & Mansouri, Z. (2025).**
*Enhancing Logic-Based Testing with EvoDomain: A Search-Based Domain-Oriented Test Suite Generation Approach.*
**Information and Software Technology, 177, 107564.**

**DOI:** [10.1016/j.infsof.2024.107564](https://doi.org/10.1016/j.infsof.2024.107564)

The article is published in *Information and Software Technology*.

## 📜 License

This project is released under the license included in this repository.
