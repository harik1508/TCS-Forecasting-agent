# AI Usage, Development and Evaluation

## 1. AI-Assisted Development

ChatGPT was used as an AI development assistant throughout this assignment.

Its contributions included:

- System architecture and technology selection.
- FastAPI and LangChain integration.
- MySQL schema and request-response logging.
- Adaptation of existing RAG components.
- Financial extraction pipeline development.
- Document discovery debugging.
- Prompt engineering and structured output design.
- Regression test development.
- Forecast quality review.
- Technical documentation.

I configured and executed the application locally, inspected intermediate outputs, validated financial figures against source documents, ran regression tests and verified database persistence.

## 2. Reused Components

The project extends my existing Earnings RAG Assistant:

https://github.com/harik1508/earnings-rag-assistant

The reused components include:

- Overlapping token-based text chunking.
- BM25 lexical retrieval.
- BGE embedding-based semantic retrieval.
- Weighted hybrid retrieval.

The TCS-specific discovery adapter, financial extraction pipeline, comparative-table fallback, forecasting workflow, structured response schemas and MySQL logging were developed for this assignment with AI assistance.

Previous project evaluation metrics are not presented as results of this assignment.

## 3. Runtime AI Components

| Component | Purpose |
|---|---|
| GPT-4o-mini | Qualitative forecasting and structured synthesis |
| GPT-4o-mini fallback | Extraction of missing financial metrics |
| BGE-small-en-v1.5 | Semantic text embeddings |
| LangChain StructuredTool | Specialized tool interfaces |
| Pydantic | Structured output validation |

The financial parser prioritizes deterministic extraction rather than relying exclusively on an LLM.

Both specialized tools are explicitly invoked by the master agent to ensure complete analysis.

## 4. Development Challenges and Solutions

### Document Discovery Failure

The initial discovery implementation failed because the live Screener HTML structure differed from the original assumptions.

The discovery adapter was updated to parse the actual earnings-call section, convert announcement months into quarter-end dates, derive financial periods from official report URLs and reject mismatched historical transcripts.

Regression tests were added for these scenarios.

### Incomplete Financial Extraction

The initial LLM-based financial extractor recovered only one of nine required metrics.

Investigation showed that source PDFs contained different monetary units, complex tables and irregular spacing introduced during PDF text extraction.

A deterministic financial parser was introduced, improving extraction coverage to eight of nine metrics.

The remaining June net profit figure was recovered using a subsequent quarter's comparative financial table, achieving nine of nine metrics.

### Incorrect Financial Narrative Units

An early generated forecast incorrectly described INR crore values as millions.

Historical financial narratives were moved from LLM generation to deterministic Python formatting, preserving correct units and calculated growth rates.

### Weak Qualitative Citations

Some early forecasts cited introductory transcript pages or evidence that did not directly support the associated claims.

Introductory chunks were filtered and the master prompt was strengthened to require relevant citations, distinguish analyst questions from management statements and preserve uncertainty.

Semantic citation accuracy remains a limitation because evidence ID validation alone cannot establish entailment.

### Unsupported Numerical Forecasts

A later forecast generated a numerical revenue estimate without a documented forecasting methodology.

The master prompt was refined to prioritize qualitative directional forecasts and prohibit unsupported numerical predictions.

This is a prompt-level guardrail rather than a guarantee of numerical forecast exclusion.

## 5. Evaluation Methodology

Financial extraction was evaluated against nine manually identified reference values from three TCS quarterly fact sheets.

The evaluation checked:

- Correct financial period.
- Correct metric value.
- Correct monetary or percentage unit.
- Source evidence availability.
- Cross-report provenance.
- Whether LLM fallback was required.

Discovery tests used synthetic HTML fixtures covering expected behavior and failure scenarios.

API integration was evaluated by executing live forecast requests and verifying the stored MySQL records.

Qualitative output was manually inspected for evidence relevance, management attribution, unsupported claims and appropriate uncertainty.

## 6. Observed Results

| Evaluation metric | Result |
|---|---|
| Source documents processed | 6 |
| Financial quarters analyzed | 3 |
| Initial extraction coverage | 1/9 (11.11%) |
| Deterministic direct extraction | 8/9 (88.89%) |
| Final extraction coverage | 9/9 (100%) |
| Extraction coverage improvement | 88.89 percentage points |
| Reference value accuracy | 9/9 |
| Financial evidence coverage | 9/9 |
| LLM fallback calls in financial validation | 0 |
| Discovery regression tests | 16/16 passed |
| Initial successful API requests | 4/4 |
| Initial valid stored JSON pairs | 4/4 |
| Initial mean API execution time | 76.95 seconds |
| Dependency compatibility | Passed |
| Python compilation | Passed |

The API timing and success-rate statistics refer to an initial sample of four successful integration requests.

The final financial extraction results apply to the evaluated three-quarter dataset only.

## 7. Guardrails

The implementation incorporates:

- Deterministic extraction and financial calculations.
- Comparative-table fallback with source provenance.
- Structured LLM extraction for missing values.
- Source quote validation.
- Explicit financial units.
- Pydantic request and response schemas.
- Evidence ID validation and bounded retries.
- Independent retrieval across financial quarters.
- Introductory transcript filtering.
- Instructions against document-based prompt injection.
- Conditional forecasting language.
- Accounting comparability disclosures.
- Qualitative confidence reporting.

## 8. Remaining Limitations

- Semantic entailment is not automatically verified.
- Management and analyst statements are not separated using a dedicated speaker-aware parser.
- Prompt-level guardrails may not eliminate every unsupported forecast.
- Accounting adjustments are disclosed generally rather than attached to every affected metric.
- No formal TCS-specific retrieval recall or faithfulness benchmark has been completed.
- Failure-path API logging has not been independently integration-tested.
- Framework-level invalid requests are not logged.
- Future financial reports may require parser adaptations.
- Website availability and HTML structure may affect discovery.
- The observed API execution results are not representative of production-scale load.

No unmeasured retrieval accuracy, forecast accuracy or production reliability metrics are claimed.

## 9. Reproducibility

The repository includes:

- Source code.
- Environment variable template.
- Docker Compose configuration.
- Dependency requirements.
- Example request.
- Actual API response.
- Discovery regression tests.
- Financial validation script.
- Generated evaluation reports.

The OpenAI API key, downloaded document cache and local virtual environment are excluded from version control.