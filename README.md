# Breathe ESG - Carbon Accounting Engine

Breathe ESG is a modern, full-stack enterprise carbon accounting prototype designed to ingest unstructured data from multiple sources (SAP, Utilities, Corporate Travel), normalize it against standard emission factors, flag anomalies, and provide an immutable audit trail for legal compliance.

## Architecture

* **Frontend:** React, TailwindCSS, Vite (Hosted on Vercel)
* **Backend:** Python, Django REST Framework, SQLite/PostgreSQL (Hosted on Railway)
* **API Proxy:** The frontend proxies all `/api` requests through Vercel to bypass ISP DNS blocking.

## Core Features
- **Multi-source Ingestion Engine:** Parses Tab-delimited TXT (SAP) and CSV (Utility, Travel) files.
- **Automated Normalization:** Maps raw quantities to standard emission factors (Scope 1, 2, 3).
- **Anomaly Detection:** Hard-coded heuristics catch massive outliers or negative consumption values to prevent bad data from polluting the ledger.
- **Human-in-the-Loop Review:** A clean dashboard for Analysts to review, edit, and approve flagged records.
- **Role-Based Access Control (RBAC):** Public links default to a Read-Only Auditor view. Analysts must log in to mutate state.
- **Immutable Audit Trail:** All edits generate an immutable before/after snapshot log of the exact data change and the user responsible.

## Project Documentation Deliverables
The core architectural decisions and research are documented in the `docs/` folder. These files carry significant weight in evaluating the platform's enterprise readiness:

1. [Data Model Architecture (`docs/MODEL.md`)](./docs/MODEL.md): Explains how multi-tenancy, Scope categorization, source-of-truth tracking, and the audit trail are structurally handled.
2. [Design Decisions (`docs/DECISIONS.md`)](./docs/DECISIONS.md): Details how ambiguities were resolved (unmatched data, anomaly definitions, workflows) and what questions remain for Product Managers.
3. [Engineering Tradeoffs (`docs/TRADEOFFS.md`)](./docs/TRADEOFFS.md): Outlines three deliberate omissions made to optimize prototype delivery speed over production scale.
4. [Data Sources Research (`docs/SOURCES.md`)](./docs/SOURCES.md): Explores the real-world formatting of SAP, Utility, and Travel data, what we chose to sample, and what edge cases would break the current ingestion engine in production.

## Local Setup

### Backend (Django)
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python seed.py
python manage.py runserver
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

### Sample Data
You can find pre-generated `sap_procurement.txt`, `utility_data.csv`, and `travel_data.csv` files in the `/sample_data` folder to test the ingestion engine.

### Demo Login
To access the "Edit" and "Approve" features, click "Login as Analyst" on the frontend:
* **Username:** `analyst`
* **Password:** `esg2024!`
