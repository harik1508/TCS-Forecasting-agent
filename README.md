# TCS Financial Forecasting Agent

An AI-powered financial research and forecasting service that automatically discovers TCS quarterly financial reports and earnings-call transcripts, extracts financial metrics, analyzes management commentary, and generates an evidence-grounded qualitative outlook for the upcoming quarter.

Built as part of the Elevation AI technical assignment.

## Key Features

- Automated discovery of the latest two or three quarterly financial reports and earnings-call transcripts.
- Deterministic financial metric extraction with comparative-table and LLM fallbacks.
- Hybrid Retrieval-Augmented Generation (RAG) using BM25 and BGE embeddings.
- Two specialized LangChain tools coordinated by a master forecasting agent.
- Structured JSON forecasts with source URLs, page references and evidence IDs.
- MySQL-based request and response logging.
- FastAPI REST endpoints and interactive Swagger documentation.
- Automated regression tests and financial extraction validation.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.10+ |
| API framework | FastAPI, Uvicorn |
| AI orchestration | LangChain StructuredTool |
| LLM | OpenAI GPT-4o-mini |
| Embedding model | BAAI/bge-small-en-v1.5 |
| Retrieval | BM25 and cosine similarity |
| Document discovery | Requests, BeautifulSoup |
| PDF extraction | pdfplumber |
| Data processing | NumPy, Python |
| Database | MySQL 8.0 |
| Database integration | SQLAlchemy, PyMySQL |
| Schema validation | Pydantic |
| Infrastructure | Docker Compose |
| Testing | pytest |

## System Architecture

```mermaid
flowchart TD
    A[User or REST Client] --> B[FastAPI]
    B --> C[MySQL Request Logging]
    C --> D[Automated Document Discovery]
    D --> E[PDF Download and Cache]
    E --> F[FinancialDataExtractorTool]
    E --> G[QualitativeAnalysisTool]
    F --> H[Master Forecasting Agent]
    G --> H
    H --> I[Structured Output Validation]
    I --> J[MySQL Final Response Logging]
    J --> K[JSON Response]
```

The master agent explicitly invokes both specialized tools before generating the final forecast. This controlled orchestration ensures that neither financial nor qualitative analysis is skipped.

The workflow uses LangChain tools and structured LLM synthesis rather than an unrestricted autonomous planning loop.

## Document Discovery and Ingestion

The discovery module retrieves document links from:

https://www.screener.in/company/TCS/consolidated/#documents

It identifies quarterly TCS fact sheets and earnings-call transcripts, maps earnings-call months to financial quarter-end dates, and validates fiscal-year information embedded in official document URLs.

The discovery logic handles:

- Indian financial-year quarter conventions.
- Reports and transcripts appearing in separate HTML rows.
- Incorrectly associated historical transcript links.
- Incomplete document pairs.
- Missing document sections.

Documents are downloaded automatically, cached locally by URL hash and parsed using pdfplumber. The application does not require manually uploaded PDFs.

## Specialized Tools

### 1. FinancialDataExtractorTool

Extracts the following consolidated financial metrics:

- Revenue from operations, expressed in INR crore.
- Net profit, expressed in INR crore.
- Operating margin, expressed as a percentage.

The extraction pipeline follows three stages:

1. Deterministic extraction from the current quarter's fact sheet.
2. Comparative-table extraction from a subsequent quarter's fact sheet when a required metric is unavailable.
3. Structured LLM extraction as a fallback for remaining missing metrics.

Extracted values are associated with source URLs, page numbers, source quotes and extraction methods.

Python calculates sequential revenue growth, net profit growth and operating margin changes. Monetary values are normalized to INR crore, while margin changes are expressed in percentage points.

Unverifiable or unavailable metrics remain null rather than being fabricated.

### 2. QualitativeAnalysisTool

Uses a hybrid RAG pipeline to retrieve relevant management commentary from earnings-call transcripts.

The pipeline consists of:

1. Page-level PDF text extraction.
2. Overlapping token-based chunking.
3. BGE-small-en-v1.5 embedding generation.
4. BM25 lexical retrieval.
5. Cosine similarity-based semantic retrieval.
6. Weighted hybrid retrieval.
7. Evidence collection across quarters and business topics.

Each quarter is indexed independently to improve cross-quarter coverage.

The retrieval topics include revenue and demand, profitability, deal momentum, AI adoption, management outlook and business risks.

The user's query is also used as an additional retrieval query.

A separate vector database is unnecessary for the current document collection. Cross-encoder reranking is not enabled.

## Master Forecasting Agent

The master agent combines the outputs of both specialized tools and generates a structured qualitative forecast using OpenAI GPT-4o-mini.

The output includes:

- Historical financial trends.
- Management sentiment.
- Recurring business themes.
- Forward-looking management commentary.
- Revenue outlook.
- Operating margin outlook.
- Risks and opportunities.
- Base-case forecast.
- Qualitative confidence and rationale.
- Limitations and source evidence.

Historical financial statements are generated deterministically in Python to prevent numerical transcription and currency conversion errors.

The master prompt instructs the model to distinguish historical facts, management statements and analytical forecasts, avoid unsupported numerical projections, preserve uncertainty and cite relevant evidence.

The master prompt and orchestration logic are available in `app/agent.py`. The specialized tools are implemented in `app/tools.py`.

## Project Structure

```text
tcs-financial-forecasting-agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py
│   ├── discovery.py
│   ├── financial_parser.py
│   ├── schemas.py
│   └── tools.py
├── ingestion/
│   └── chunking.py
├── retrieval/
│   └── hybrid_search.py
├── tests/
│   └── test_discovery.py
├── examples/
│   ├── request.json
│   └── forecast_response.json
├── reports/
│   ├── financial_validation.txt
│   └── test_results.xml
├── test_financial_tool.py
├── validate_documents.py
├── compose.yaml
├── requirements.txt
├── .env.example
├── .gitignore
├── AI_USAGE.md
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.10 or 3.11
- Docker Desktop with Docker Compose
- Git
- Internet access
- OpenAI API key with API billing enabled

The application was locally tested using Python 3.10.11 and MySQL 8.0.46 on Windows.

### Step 1: Clone the repository

```bash
git clone https://github.com/harik1508/tcs-financial-forecasting-agent.git
cd tcs-financial-forecasting-agent
```

### Step 2: Create a virtual environment

Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Configure environment variables

Windows:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Configure `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
MYSQL_URL=mysql+pymysql://forecast:forecast_dev@127.0.0.1:3307/forecast
```

The database credentials are local development defaults. Never commit the actual `.env` file or API key.

### Step 5: Start MySQL

Ensure Docker Desktop is running.

```bash
docker compose up -d
docker compose ps
```

Wait until MySQL is healthy.

The database is exposed through port 3307 to avoid conflicts with existing MySQL installations.

### Step 6: Start FastAPI

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The application creates the required database table automatically.

Swagger UI:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

The first forecast may take longer because the embedding model and source documents must be downloaded.

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Database connectivity check |
| POST | `/api/v1/forecast` | Generate a TCS forecast |
| GET | `/api/v1/forecasts/{request_id}` | Retrieve a stored forecast record |

### Example Request

```json
{
  "company": "TCS",
  "quarters": 3,
  "query": "Analyze the latest three quarters of TCS financial performance and earnings call transcripts. Forecast the upcoming quarter, highlighting revenue trends, profitability, management outlook, growth opportunities and key risks."
}
```

The `quarters` parameter supports two or three quarters.

### Execute from PowerShell

```powershell
Invoke-WebRequest `
    -Uri "http://127.0.0.1:8000/api/v1/forecast" `
    -Method POST `
    -ContentType "application/json" `
    -InFile "examples/request.json" `
    -TimeoutSec 300 `
    -UseBasicParsing `
    -OutFile "examples/forecast_response.json"
```

### Example Response

A complete response generated by the running application is available in:

`examples/forecast_response.json`

The response contains a unique request ID, execution status, analyzed quarters, target quarter, financial metrics, forecast, source evidence and execution metadata.

## Database Logging

The application stores valid forecast requests and their execution results in the MySQL `forecast_logs` table.

| Column | Type |
|---|---|
| request_id | VARCHAR(36), primary key |
| request_payload | JSON |
| response_payload | JSON |
| status | VARCHAR(20) |
| error_message | TEXT |
| execution_time_ms | INT |
| created_at | DATETIME |

The application creates a running record before processing the forecast and updates it with the final status and response.

Inspect the database:

```bash
docker compose exec mysql mysql -uforecast -pforecast_dev forecast
```

```sql
SELECT request_id, status, execution_time_ms, created_at
FROM forecast_logs
ORDER BY created_at DESC;
```

Validate stored JSON:

```sql
SELECT
    request_id,
    JSON_VALID(request_payload) AS valid_request,
    JSON_VALID(response_payload) AS valid_response
FROM forecast_logs
WHERE status = 'success';
```

## Evaluation and Testing

### Financial Extraction Results

The evaluation dataset contains three quarterly TCS fact sheets and three earnings-call transcripts covering March, June and September 2026.

| Metric | Q4 FY26 | Q1 FY27 | Q2 FY27 |
|---|---:|---:|---:|
| Revenue (INR crore) | 70,698 | 72,275 | 73,188 |
| Net profit (INR crore) | 13,718 | 13,849 | 13,884 |
| Operating margin (%) | 25.3 | 24.0 | 24.0 |
| Revenue QoQ (%) | — | 2.23 | 1.26 |
| Net profit QoQ (%) | — | 0.95 | 0.25 |
| Margin change (percentage points) | — | -1.30 | 0.00 |

The June 2026 net profit was recovered from the September 2026 comparative table. The June profit figure excludes exceptional items. The figures follow the fact-sheet presentation basis and should not automatically be interpreted as unadjusted statutory figures.

### Extraction Improvement

| Implementation | Metrics extracted | Coverage |
|---|---:|---:|
| Initial LLM-based extraction | 1/9 | 11.11% |
| Deterministic direct extraction | 8/9 | 88.89% |
| Deterministic extraction with comparative fallback | 9/9 | 100% |

The final financial extraction validation matched all nine reference values and required zero LLM fallback calls for this dataset.

These results demonstrate extraction performance on the evaluated reports, not guaranteed accuracy on future documents.

### Observed Test Results

| Evaluation | Result |
|---|---|
| Discovery regression tests | 16/16 passed |
| Unit test execution time | 0.38 seconds |
| Financial reference value accuracy | 9/9 |
| Financial evidence coverage | 9/9 |
| Cross-report provenance | Passed |
| Python compilation | Passed |
| Dependency compatibility | Passed |
| Initial API integration evaluation | 4/4 successful requests |
| Initial MySQL JSON validation | 4/4 valid request and response pairs |
| Mean API execution time for initial four runs | 76.95 seconds |
| Minimum execution time | 71.31 seconds |
| Maximum execution time | 82.44 seconds |

The timing statistics refer to the four measured integration runs, not a production load test.

### Run Tests

```bash
python -m pytest tests -v
python test_financial_tool.py
python -m compileall app ingestion retrieval
python -m pip check
```

The discovery tests use synthetic HTML fixtures and do not require OpenAI calls or live website access.

The financial validation script uses the evaluated live document collection and expected reference values. It may require updating when newer quarters become available.

Generated test reports are included in the `reports/` directory.

## Guardrails

- Structured request and response validation using Pydantic.
- Deterministic financial calculations.
- Source quote validation.
- Financial unit normalization.
- Cross-report source provenance.
- Null values for unavailable or unverifiable metrics.
- Independent retrieval for each quarter.
- Introductory transcript chunk filtering.
- Evidence ID validation with bounded retry.
- Instructions treating source documents as untrusted data.
- Conditional qualitative forecasts rather than investment recommendations.

## Limitations and Future Improvements

- Citation ID validation does not guarantee semantic entailment. Manual review identified some incorrectly attributed qualitative claims.
- Prompt instructions reduce unsupported forecasts but do not guarantee their absence.
- Financial extraction was evaluated on three specific quarters and may require adaptation to future PDF layouts.
- Some financial figures exclude exceptional items. Full metric-level accounting-basis annotation remains future work.
- Document discovery depends on live website structure and document availability.
- Scanned PDFs requiring OCR are not currently supported.
- Speaker-aware transcript parsing is not implemented.
- Framework-level invalid requests are not logged because they do not reach the forecast handler.
- Failure-path API logging is implemented but has not been independently integration-tested.
- No formal retrieval Recall@K benchmark or complete qualitative entailment benchmark has been performed for this TCS dataset.
- The application is intended for local demonstration and does not include production authentication, rate limiting or load testing.
- Live stock-market data integration is not implemented.

## AI Usage and Prior Work

This project extends my earlier Earnings RAG Assistant:

https://github.com/harik1508/earnings-rag-assistant

The overlapping chunking and hybrid retrieval components were reused and adapted for TCS-specific financial forecasting.

ChatGPT assisted with architecture design, implementation, debugging, prompt engineering, test development and documentation. The application uses OpenAI GPT-4o-mini at runtime for structured financial fallback extraction and qualitative forecast synthesis.

See `AI_USAGE.md` for detailed AI usage, validation methodology and observed limitations.

## Disclaimer

This application generates research-oriented business outlooks based on publicly available financial documents. Its forecasts are analytical interpretations, not official TCS guidance or investment recommendations.