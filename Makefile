# Task runner for enterprise-talk-to-data.
#
# Requires: poetry (https://python-poetry.org/docs/#installation)
#           make   (choco install make on Windows)
#
# PowerShell auto-detection:
#   Windows     -> powershell (Windows PowerShell 5.1, always present)
#   macOS/Linux -> pwsh (PowerShell 7)
# Override with: make env PWSH=pwsh

ifeq ($(OS),Windows_NT)
    PWSH ?= powershell
else
    PWSH ?= pwsh
endif

.PHONY: help env pdf clean-pdf install check start-backend apply-sql-views infra-init infra-apply tests

help:   ## show this help
	@echo ""
	@echo "  Setup"
	@echo "  -----"
	@echo "  install          install all dependencies via Poetry"
	@echo "  env              install deps then verify PDF toolchain"
	@echo ""
	@echo "  Docs / PDF"
	@echo "  ----------"
	@echo "  pdf              generate docs/pdf/*.pdf from Markdown sources"
	@echo "  clean-pdf        remove generated PDFs"
	@echo ""
	@echo "  Python"
	@echo "  ------"
	@echo "  check            syntax-check all .py files under src/backend/"
	@echo "  tests            run pytest against src/backend/tests/"
	@echo "  eval             run golden evaluation (MODE=fast|full, OUTPUT=path)"
	@echo "  start-backend    start the FastAPI backend server"
	@echo ""
	@echo "  SQL"
	@echo "  ---"
	@echo "  apply-sql-views  deploy analytics views to the database"
	@echo ""
	@echo "  Infrastructure  (src/infra/terraform)"
	@echo "  --------------------------------------"
	@echo "  infra-init       terraform init"
	@echo "  infra-apply      terraform apply  -- requires ENV=dev or ENV=prod"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────

install:  ## install all dependencies via Poetry (creates .venv if needed)
	poetry install

env: install   ## install deps then verify PDF toolchain (pandoc, wkhtmltopdf, mmdc)
	@echo Checking PDF toolchain:
	-@$(PWSH) -NoProfile -Command "if (Get-Command pandoc -EA 0) { '  ok   pandoc' } else { Write-Warning 'missing pandoc      -> https://pandoc.org/installing.html' }"
	-@$(PWSH) -NoProfile -Command "if (Get-Command wkhtmltopdf -EA 0) { '  ok   wkhtmltopdf' } else { Write-Warning 'missing wkhtmltopdf -> https://wkhtmltopdf.org/downloads.html' }"
	-@$(PWSH) -NoProfile -Command "if (Get-Command mmdc -EA 0) { '  ok   mmdc' } else { Write-Warning 'missing mmdc        -> npm install -g @mermaid-js/mermaid-cli' }"

# ── Docs / PDF ────────────────────────────────────────────────────────────────

pdf:       ## generate docs/pdf/*.pdf from Markdown sources
	poetry run python scripts/build_pdfs.py docs/

clean-pdf: ## remove generated PDFs
	@$(PWSH) -NoProfile -Command "Remove-Item docs/pdf/*.pdf -Force -ErrorAction SilentlyContinue; Write-Host 'Removed generated PDFs.'"

# ── Python ────────────────────────────────────────────────────────────────────

check: install  ## syntax-check all Python files under src/backend/
	poetry run python -c "import py_compile, pathlib; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('src/backend').rglob('*.py')]"

tests: install  ## run pytest against src/backend/tests/
	@set PYTHONPATH=src && poetry run pytest src/backend/tests/ -v

eval: install  ## run golden evaluation — MODE=fast|full (default fast), OUTPUT=path, LIMIT=N
	@set PYTHONPATH=src && poetry run python -m backend.evaluation_runner --mode $(or $(MODE),fast) $(if $(OUTPUT),--output $(OUTPUT),) $(if $(LIMIT),--limit $(LIMIT),)

start-backend: install  ## start the FastAPI backend server
	@set PYTHONPATH=src && poetry run python -m backend.main

# ── SQL ───────────────────────────────────────────────────────────────────────

apply-sql-views: install  ## deploy analytics views to the database
	@set PYTHONPATH=src && poetry run python src/backend/db/deploy_views.py

# ── Infrastructure ────────────────────────────────────────────────────────────

infra-init:  ## terraform init  (src/infra/terraform)
	terraform -chdir=src/infra/terraform init

infra-apply:  ## terraform apply  (ENV=dev|prod)
	@if not defined ENV (echo ENV is not set. Use ENV=dev or ENV=prod && exit 1)
	terraform -chdir=src/infra/terraform apply -parallelism=1 -var-file=envs/$(ENV)/terraform.tfvars -auto-approve
