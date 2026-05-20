# SOP: Knowledge Ingestion & Organization

**Purpose**: Ensure every piece of content compounds intelligence rather than just adding noise. Consistent process = compounding returns on knowledge.

**Applies to**: All incoming datasets, papers, notes, code snippets, ideas about quant, trading, math, finance, markets.

---

## Step-by-Step Ingestion Process

### 1. Receive Raw Material
- User provides file, text, dataset, paper, etc. (naming may be messy or irrelevant).
- Do **not** ask for clarification on content unless truly ambiguous.

### 2. Atomic Decomposition
Break the input into atomic, high-signal units:
- One idea = one note (or section)
- One dataset = structured note + metadata
- One paper = summary + critical annotations + key concepts

### 3. Categorization Decision Tree
Route content into the correct pillar:
- Mathematics Foundations → 01-Mathematics/
- Probability, Statistics & Inference → 02-Probability-Statistics/
- Quantitative Finance Core → 03-Quant-Finance-Core/
- Trading Strategies & Edges → 04-Trading-Strategies-Edges/
- Risk, Portfolio & Execution → 05-Risk-Portfolio-Execution/
- Data, Infrastructure & Implementation → 06-Data-Infrastructure/
- Behavioral & Meta → 07-Behavioral-Meta/

If it spans multiple areas → Create it in the most relevant folder **and** create synthesis links.

### 4. Quality & Synthesis Layer
For every major input, add:
- **Key Concepts** (extracted)
- **Implications for Trading Systems** (how this can be used)
- **Potential Failure Modes / Critiques**
- **Cross-Links** to existing notes (`[[wikilink]]`)
- **Anti-Cookie-Cutter Insight** (if any non-obvious lesson emerges)

### 5. Documentation
- Use clear, descriptive filenames following the pattern:
  `YYYY-MM-Topic-Subtopic.md` or `Concept-Name.md`
- Always update the relevant index or parent note.

### 6. Compounding Step (Critical)
After ingesting, ask yourself internally:
- "What new connection does this create?"
- "Does this challenge anything already in the vault?"
- Update [[00-Anti-Cookie-Cutter-Insights.md]] if a genuinely valuable insight appears.

---

## Anti-Compounding Behaviors to Avoid
- Dumping raw text without processing
- Creating overly long monolithic notes
- Ignoring cross-links
- Failing to extract implications for real trading systems

---

**Goal**: Every ingestion round should make the entire system noticeably smarter for the next reasoning task.

*Follow this SOP rigorously for maximum intelligence compounding.*
