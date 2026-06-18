# Task runner for enterprise-talk-to-data.
#
# PowerShell auto-detection:
#   Windows     -> powershell (Windows PowerShell 5.1, always present)
#   macOS/Linux -> pwsh (PowerShell 7)
# Override with: make env PWSH=pwsh
#
# On Windows, `make` must be installed (e.g. `choco install make`).

ifeq ($(OS),Windows_NT)
    PWSH        ?= powershell
    VENV_PYTHON := .venv\Scripts\python.exe
else
    PWSH        ?= pwsh
    VENV_PYTHON := .venv/bin/python
endif

PYTHON := python

.PHONY: help env pdf clean-pdf venv install check start-backend apply-sql-views infra-init infra-apply tests

help:   ## show this help
	@echo ""
	@echo ""
	@echo "  Setup"
	@echo "  -----"
	@echo "  env              create .venv, install requirements, verify PDF toolchain"
	@echo ""
	@echo "  Docs / PDF"
	@echo "  ----------"
	@echo "  pdf              generate docs/pdf/*.pdf from Markdown sources"
	@echo "  clean-pdf        remove generated PDFs"
	@echo ""
	@echo "  src/"
	@echo "    Python"
	@echo "    ------"
	@echo "    check            syntax-check all .py files under src/backend/"
	@echo "    tests            run pytest against src/backend/tests/"
	@echo "    start-backend    start the FastAPI backend server"
	@echo ""
	@echo "    SQL"
	@echo "    ---"
	@echo "    apply-sql-views  deploy analytics views to the database"
	@echo ""
	@echo "    Infrastructure  (src/infra/terraform)"
	@echo "    ----------------------------------------"
	@echo "    infra-init       terraform init"
	@echo "    infra-apply      terraform apply  -- requires ENV=dev or ENV=prod"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────

env: install   ## install deps then verify PDF toolchain (pandoc, wkhtmltopdf, mmdc)
	@echo Checking PDF toolchain:
	-@$(PWSH) -NoProfile -Command "if (Get-Command pandoc -EA 0) { '  ok   pandoc' } else { Write-Warning 'missing pandoc      -> https://pandoc.org/installing.html' }"
	-@$(PWSH) -NoProfile -Command "if (Get-Command wkhtmltopdf -EA 0) { '  ok   wkhtmltopdf' } else { Write-Warning 'missing wkhtmltopdf -> https://wkhtmltopdf.org/downloads.html' }"
	-@$(PWSH) -NoProfile -Command "if (Get-Command mmdc -EA 0) { '  ok   mmdc' } else { Write-Warning 'missing mmdc        -> npm install -g @mermaid-js/mermaid-cli' }"

# ── Docs / PDF ────────────────────────────────────────────────────────────────

pdf:       ## generate docs/pdf/*.pdf from Markdown sources
	$(VENV_PYTHON) scripts/build_pdfs.py docs/

clean-pdf: ## remove generated PDFs
	@$(PWSH) -NoProfile -Command "Remove-Item docs/pdf/*.pdf -Force -ErrorAction SilentlyContinue; Write-Host 'Removed generated PDFs.'"

# ── src/ — Python ─────────────────────────────────────────────────────────────

venv:   ## create Python virtual environment at .venv/
ifeq ($(OS),Windows_NT)
	@if not exist ".venv\Scripts\python.exe" ($(PYTHON) -m venv .venv) else (echo Virtual environment already exists.)
else
	@test -f .venv/bin/python || $(PYTHON) -m venv .venv
endif

install: venv  ## install Python dependencies from requirements.txt
	$(VENV_PYTHON) -m pip install --no-cache-dir -r requirements.txt

check: install  ## syntax-check all Python files under src/backend/
	$(VENV_PYTHON) -c "import py_compile, pathlib; [py_compile.compile(str(p), doraise=True) for p in pathlib.Path('src/backend').rglob('*.py')]"

tests: install  ## run pytest against src/backend/tests/
	@set PYTHONPATH=src && $(VENV_PYTHON) -m pytest src/backend/tests/ -v

start-backend: install  ## start the FastAPI backend server
	@set PYTHONPATH=src && $(VENV_PYTHON) -m backend.main

# ── src/ — SQL ────────────────────────────────────────────────────────────────

apply-sql-views: install  ## deploy analytics views to the database
	$(VENV_PYTHON) src\backend\db\deploy_views.py

# ── src/ — Infrastructure ─────────────────────────────────────────────────────

infra-init:  ## terraform init  (src/infra/terraform)
	terraform -chdir=src/infra/terraform init

infra-apply:  ## terraform apply  (ENV=dev|prod)
	@if not defined ENV (echo ENV is not set. Use ENV=dev or ENV=prod && exit 1)
	terraform -chdir=src/infra/terraform apply -parallelism=1 -var-file=envs/$(ENV)/terraform.tfvars -auto-approve
