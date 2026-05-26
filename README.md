# Breathe ESG Platform

A Django REST + React application for carbon accounting data ingestion, normalization, and review.

## Architecture Summary
Breathe ESG utilizes a **Django 4.2 / Django REST Framework** backend to handle complex ingestion parsing, unit normalization, and strict append-only audit logging via PostgreSQL. The frontend is a modern **React 18** application built with Vite and Tailwind CSS, providing ESG analysts with an intuitive dashboard to review, flag, and approve emission records securely. The architecture strictly separates raw, immutable payloads from normalized operational data to ensure financial-grade auditability.

## Live URLs & Login (Deployment via user)
-   **Frontend URL:** [Pending Vercel Deployment]
-   **Backend URL:** [Pending Railway Deployment]
-   **Demo Analyst Account:**
    -   Email / Username: `analyst`
    -   Password: `esg2024!`

## How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or fallback to SQLite via `.env`)

### 1. Backend Setup
```bash
cd breathe_esg/backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt # (or install django djangorestframework psycopg2-binary django-cors-headers python-dotenv)

# Setup DB and Seed Data
python manage.py migrate
python seed.py
python manage.py runserver 8000
```

### 2. Frontend Setup
```bash
cd breathe_esg/frontend
npm install
npm run dev
```
The app will run at `http://localhost:5173`.

### 3. Testing the App
1. Log in (or simply navigate to the app, local prototype bypasses strict auth for ease of demo).
2. Go to **Ingest**.
3. Upload the generated files located in `breathe_esg/sample_data/`.
4. Go to **Review** to see normalized, flagged, and calculated records.
