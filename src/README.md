# Enterprise Talk to Data

A natural-language-to-SQL pipeline for newspaper analytics. Users ask plain-English questions; the system classifies intent, selects the right database views, generates and validates SQL, executes it, and returns a natural-language answer — all through a single `/ask` endpoint.

## How it works

```
POST /api/v0/ask  {"question": "Which articles had the most comments last week?"}
```

The request passes through 7 sequential stages. Each stage either passes control to the next (`None`), stops the pipeline with a user-facing refusal (`Refusal`), or — in the final stage — returns the answer (`Success`).

| # | Stage | LLM | Refuses when |
|---|---|---|---|
| 1 | **Intent** | schema_retrieval | question is out of scope, off-domain, or requires external data |
| 2 | **View selection** | schema_retrieval | confidence < 0.4, or no relevant view identified |
| 3 | **Metadata** | — | no schema/metrics metadata found for the selected views |
| 4 | **SQL generation** | sql_generation | LLM returns no query or unparseable JSON |
| 5 | **SQL validation** | — | query violates safety rules (see below) |
| 6 | **Execution** | — | database unavailable or query errors |
| 7 | **Answer** | summary | never refuses — falls back to row count if LLM unavailable |

**SQL safety rules (stage 5):** SELECT only · `analytics.*` views only · no DDL/DML · no multi-statement · `TOP`/`LIMIT` required (max 500 rows).

## Repository layout

```
src/
  backend/
    app/
      api/           — FastAPI routes (/ask, /metadata/*, /articles, …)
      core/          — config, logger, SQL safety validator
      db/            — Azure SQL connection and query execution
      evaluation/    — golden runner: replays curated questions, checks answerability
      models/        — Pydantic API models, PipelineContext, TraceRecord
      prompts/       — versioned prompt builders (intent, view selection, SQL gen, answer)
      services/      — LLMService (Azure OpenAI), metadata loader, pipeline composer
      stages/        — one file per pipeline step: service + stage + result type
    tests/
      integration/   — endpoint smoke tests (requires running server)
      test_*.py      — unit tests (87 tests, no external dependencies)
  metadata/
    schema_descriptions/  — column-level view documentation (YAML)
    metrics/              — view purpose, business meaning, limitations (YAML)
    glossary/             — domain term definitions (YAML)
    example_questions/    — golden questions for evaluation
  sql/               — view DDL and security scripts
  infra/             — Terraform modules for Azure deployment
```

## Configuration

Copy `.env.example` to `.env` and fill in:

```env
# Azure SQL
AZURE_SQL_SERVER=
AZURE_SQL_DATABASE=
AZURE_SQL_USERNAME=
AZURE_SQL_PASSWORD=

# Azure OpenAI — one endpoint, three task-specific deployments (no shared default)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_SCHEMA_RETRIEVAL_DEPLOYMENT=   # intent + view selection (lightweight model)
AZURE_OPENAI_SQL_GENERATION_DEPLOYMENT=     # SQL generation (reasoning-capable model)
AZURE_OPENAI_SUMMARY_DEPLOYMENT=            # answer generation (instruction-following model)
```

Three separate deployments are required — the pipeline uses different model tiers per task by design. Using the same deployment name for all three is valid for local development.

If you provisioned infrastructure with Terraform, retrieve these values from its outputs:

```powershell
terraform -chdir=src/infra/terraform output   # shows endpoint and deployment names
```

## Running locally

**Prerequisites:** Python 3.11+, `make` (`choco install make` on Windows).

```powershell
# 1. Create virtual environment and install dependencies
make install

# 2. Configure environment
copy .env.example .env
# Edit .env with Azure SQL and Azure OpenAI credentials

# 3. Deploy SQL views to the database (first time or after view changes)
make apply-sql-views

# 4. Start the backend
make start-backend
```

The API is then available at `http://localhost:8000`.

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Interactive Swagger UI |
| `http://localhost:8000/api/v0/ask` | Main pipeline endpoint (POST) |
| `http://localhost:8000/api/v0/metadata/views` | Schema descriptions |
| `http://localhost:8000/api/v0/metadata/metrics` | Metrics metadata |
| `http://localhost:8000/api/v0/metadata/glossary` | Domain glossary |

**Example request:**

```bash
curl -X POST http://localhost:8000/api/v0/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which articles had the most comments last week?"}'
```

## Testing

```powershell
make tests   # 87 unit tests, no external dependencies required
make eval    # golden runner — requires a live .env with Azure OpenAI credentials
```

The unit tests mock all external dependencies (LLM, database) and run fully offline.

The golden runner (`evaluation/golden_runner.py`) replays the questions in `metadata/example_questions/golden_questions.yml` through the intent and view-selection stages against a live LLM and asserts correct answerability and domain classification.

## Infrastructure

Terraform provisions the Azure resources needed to run the pipeline. **Azure SQL is not managed by Terraform** and must be provisioned separately.

### Resources created

| Resource | Name | Purpose |
|---|---|---|
| Resource Group | `rg-lefigaro-talk2data-{env}` | Container for all project resources |
| Azure OpenAI account | `openai-lefigaro-{env}` | Cognitive Services endpoint (SKU S0) |
| OpenAI deployment | `talk2data-gpt41mini-schema-retrieval` | Used by intent classification and view selection stages |
| OpenAI deployment | `talk2data-gpt41mini-sql-generation` | Used by SQL generation stage |
| OpenAI deployment | `talk2data-gpt41mini-summary` | Used by answer generation stage |

Default model for all three deployments is `gpt-4.1-mini`. Override per deployment via Terraform variables (`schema_retrieval_model`, `sql_generation_model`, `summary_model`).

### Deploying

Create a tfvars file for your target environment:

```
src/infra/terraform/envs/dev/terraform.tfvars
src/infra/terraform/envs/prod/terraform.tfvars
```

Required variables: `subscription_id`, `tenant_id`, `client_id`, `user_object_id`. Optional overrides: `location` (default `eastus`), `resource_group_name`, `openai_account_name`, model names.

```powershell
make infra-init          # terraform init
make infra-apply ENV=dev  # deploy to dev
make infra-apply ENV=prod # deploy to prod
```

After apply, retrieve the OpenAI endpoint and deployment names to populate your `.env`:

```powershell
terraform -chdir=src/infra/terraform output
```
