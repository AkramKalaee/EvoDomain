# EvoDomain

**Search-based domain-oriented test suite generation for logic-based testing**

EvoDomain is a search-based testing approach that extends conventional logic-based coverage with **domain-oriented test generation**. It targets faults that may remain undetected when test generation focuses only on logical conditions and decisions, by explicitly searching for **feasible subdomains and their boundaries**.

> **Research project:** EvoDomain was developed and evaluated as part of our research on automated test generation and domain-oriented testing.

---

## 🎯 Why EvoDomain?

Logic-based coverage criteria such as **MC/DC** are effective at exercising the logical structure of predicates, but they do not necessarily reveal faults that alter the underlying input domain.

A predicate may contain multiple feasible subdomains, while achieving full logical coverage does not guarantee that every one of these subdomains has been exercised.

EvoDomain addresses this limitation by explicitly searching for feasible subdomains and their boundaries, and incorporating boundary-oriented test data into a logic-based test suite.

> **The key idea:** Don't only ask whether a condition has been exercised — explore whether all feasible regions of its input domain have been tested.

---

## 🔬 Approach

EvoDomain combines search-based optimization, domain analysis, and test-suite construction to identify diverse boundary test data.

The main workflow is:

1. **Analyze the subject program** and its predicates.
2. **Identify feasible subdomains** induced by predicate constraints.
3. **Search for domain boundaries** using a memetic search strategy.
4. **Improve candidate solutions locally** to refine boundary locations.
5. **Cluster candidate solutions** using DBSCAN to identify disconnected subdomains and preserve diversity.
6. **Generate boundary-oriented test data** from the discovered domains.
7. **Augment logic-based test suites** with the generated tests.
8. **Evaluate domain coverage and fault detection** against established approaches.

### Architecture

<p align="center">
  <img src="docs/images/diagram.png" alt="EvoDomain architecture" width="780">
</p>

<p align="center">
  <em>Overview of the EvoDomain domain-oriented test suite generation approach.</em>
</p>

---

## 🧬 Boundary-Oriented Search

At the core of EvoDomain is a **memetic search strategy**, combining evolutionary search with local improvement to efficiently locate domain boundaries.

The search is designed to discover feasible regions rather than simply generate arbitrary input values. DBSCAN is then used to identify disconnected subdomains and retain a diverse set of boundary candidates.

<table>
  <tr>
    <td align="center">
      <img src="docs/images/ex1.gif" alt="EvoDomain domain generation example 1" width="400"><br>
      <em>Domain generation example 1.</em>
    </td>
    <td align="center">
      <img src="docs/images/ex2.gif" alt="EvoDomain domain generation example 2" width="400"><br>
      <em>Domain generation example 2.</em>
    </td>
  </tr>
</table>

---

# 📊 Experimental Results

EvoDomain was evaluated on **30 subjects**, including **11 classic** and **19 industrial** case studies.

The evaluation examines whether EvoDomain can:

* efficiently identify feasible subdomains;
* achieve complete domain coverage;
* improve fault detection;
* and provide benefits beyond conventional logic-based test generation.

---

## Search Effectiveness

We compared EvoDomain with **Random Search (RS)** for identifying feasible domains.

To provide a fair comparison, Random Search was given **twice the time budget** of EvoDomain and used the same DBSCAN clustering procedure for detecting disconnected subdomains.

Both approaches were able to identify the target subdomains, but EvoDomain reached effective solutions substantially faster. Random Search required up to **four times the test budget** to reach comparable solutions.

These results show that domain-oriented test generation is not simply a matter of generating more random tests: **effective search guidance is critical for reaching useful domain boundaries efficiently.**

<p align="center">
  <img src="docs/images/search-effectiveness.png" alt="Search effectiveness comparison between EvoDomain and Random Search" width="760">
</p>

<p align="center">
  <em>Search effectiveness comparison between EvoDomain and Random Search for feasible-domain identification.</em>
</p>

---

## Domain Coverage

The subjects contain predicates with between **1 and 8 feasible subdomains**. We therefore evaluate not only conventional logical coverage, but also whether a test suite exercises each feasible subdomain at least once.

The results highlight an important limitation of conventional criteria: **full MC/DC coverage does not necessarily imply complete domain coverage**.

EvoDomain achieved **100% domain coverage across all evaluated cases**, while the MC/DC- and RoRG-based approaches failed to identify all feasible subdomains in several cases.

This distinction is important because missing a feasible subdomain can leave parts of the input space completely untested, even when the corresponding predicate satisfies a conventional logical coverage criterion.

<p align="center">
  <img src="docs/images/domain-coverage.png" alt="Domain coverage comparison between EvoDomain and baseline approaches" width="760">
</p>

<p align="center">
  <em>Domain coverage achieved by EvoDomain compared with conventional logic-based test generation approaches.</em>
</p>

### Statistical Analysis

To assess whether the observed fault-detection improvements were statistically meaningful, we used the **Wilcoxon rank-sum test** and **Vargha and Delaney's A<sub>12</sub> statistic**.

The Wilcoxon test was used to assess statistical significance without assuming normality or equal variances, while A<sub>12</sub> was used to quantify effect size.

EvoDomain showed a statistically significant difference (**p < 0.05**) compared with MC/DC for **all 30 subjects**. Compared with RoRG, EvoDomain performed significantly better for **19 of the 30 subjects**, with no statistically significant difference for the remaining 11 subjects.

---

## Fault Detection

The ultimate goal of test generation is not merely to achieve coverage, but to **expose faults**.

EvoDomain was evaluated against conventional approaches across multiple fault types, including:

* **ROR** — Relational Operator Replacement
* **CSM** — Computational Shift Mutation
* **RVM** — Relational Variable Mutation
* **AOR** — Arithmetic Operator Replacement
* **LOR** — Logical Operator Replacement
* **SD** — Statement Deletion

Across **114 subject–fault-type cases**, EvoDomain achieved the highest fault detection in **74 cases**.

More importantly, EvoDomain outperformed the compared approaches across **all evaluated fault categories**. The strongest improvement was observed for **Arithmetic Operator Replacement (AOR)** faults, which are particularly challenging for conventional logical coverage because arithmetic changes can alter the internal boundaries of predicate domains without necessarily changing the logical structure exercised by the test suite.

EvoDomain increased the average fault detection associated with MC/DC from **7.78% to 68.89%**, and with RoRG from **2.22% to 66.33%**.

<p align="center">
  <img src="docs/images/fault-detection-rate.png" alt="Average fault detection rate by fault type" width="760">
</p>

<p align="center">
  <em>Average fault detection rate of the selected approaches across different fault types.</em>
</p>

---

## 🏆 Key Findings

| Finding                                           |        Result |
| ------------------------------------------------- | ------------: |
| Subjects evaluated                                |        **30** |
| Classic subjects                                  |        **11** |
| Industrial subjects                               |        **19** |
| Feasible subdomains per predicate                 |       **1–8** |
| Domain coverage achieved by EvoDomain             |      **100%** |
| Cases with highest fault detection by EvoDomain   |  **74 / 114** |
| Improvement over MC/DC in fault detection         |    **74.44%** |
| Improvement over RoRG in fault detection          |    **65.06%** |
| Maximum fault-type support over MC/DC             |    **68.89%** |
| Maximum fault-type support over RoRG              |    **66.33%** |
| Convergence effectiveness improvement over COSMOS |       **32%** |
| Accuracy across predicate subjects                | **0.99–1.00** |
| F1-score across predicate subjects                | **0.99–1.00** |

---

## 🧪 Evaluation Artifacts

The repository contains experimental implementations, subject programs, domain-generation results, control-flow analysis components, and evaluation notebooks.

### Evaluation notebooks

* `Evaluation measurements.ipynb`
* `Postprocessing.ipynb`

These notebooks contain the analysis and post-processing used to examine the experimental results.

---

## 📁 Repository Structure

```text
EvoDomain/
│
├── docs/
│   └── images/
│       ├── diagram.png
│       ├── ex1.gif
│       ├── ex2.gif
│       ├── search-effectiveness.png
│       ├── domain-coverage.png
│       └── fault-detection-rate.png
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

| Component                 | Purpose                                    |
| ------------------------- | ------------------------------------------ |
| `src/domain/`             | Domain and boundary analysis               |
| `src/GA/`                 | Evolutionary and local search              |
| `src/domain/mcmc/`        | MCMC-based domain exploration              |
| `src/domain/multi_swarm/` | Multi-swarm search components              |
| `src/cfg/`                | Control-flow graph analysis                |
| `src/code_coverage/`      | Path and coverage analysis                 |
| `src/instrument/`         | Program instrumentation                    |
| `src/sut/`                | Subject programs                           |
| `experiments/`            | Experimental data and intermediate results |

---

## ⚙️ Installation

EvoDomain was originally developed and evaluated using **Python 3.6.4**.

Clone the repository:

```bash
git clone https://github.com/IUST-EXPERT/EvoDomain.git
cd EvoDomain
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

The current `requirements.txt` specifies the required package names without version pins because the exact historical dependency versions of the original Python 3.6 environment are no longer available.

---

## ▶️ Usage

The main entry point is:

```bash
python src/main.py
```

The repository also contains individual implementations for domain analysis, evolutionary search, instrumentation, control-flow analysis, and subject programs that can be explored independently.

---

## 🔭 Research Contribution

EvoDomain investigates a fundamental limitation of conventional logic-based testing:

> **Logical coverage does not necessarily imply adequate coverage of the underlying input domain.**

By explicitly searching for feasible subdomains and their boundaries, EvoDomain introduces a complementary perspective on test adequacy — one that considers **where the behavior changes in the input domain**, rather than only whether logical conditions have been exercised.

This work forms part of a broader research direction on **domain-oriented and behavioral testing of complex software and autonomous systems**.

---

## 📄 Publication

**Kalaee, A., Parsa, S., & Mansouri, Z. (2025).**
*Enhancing logic-based testing with EvoDomain: A search-based domain-oriented test suite generation approach.*
**Information and Software Technology, 177, 107564.**

DOI: `10.1016/j.infsof.2024.107564`

---

## 📜 License

See the `LICENSE` file for licensing information.
