# Engineering Tradeoffs

During this rapid prototype development, three specific features were deliberately excluded or simplified to optimize for speed of delivery while proving the core normalization and auditability engines.

## 1. Asynchronous Task Queues (Celery/Redis)
**What was omitted:** I did not implement an asynchronous task queue (like Celery) for the file ingestion process. Currently, files are processed synchronously in the Django view.
**Why:** Adding Redis and Celery introduces significant infrastructure complexity for a prototype. While synchronous processing is an anti-pattern for large files (it blocks the HTTP response and risks timeouts), the sample datasets are small (<100 rows). In a real production environment with 50MB SAP dumps, this would be refactored into a background worker immediately.

## 2. Advanced Machine Learning Anomaly Detection
**What was omitted:** The anomaly detection relies on simple, hard-coded heuristic thresholds (e.g., flagging negative numbers or extremely large quantities) rather than a statistical ML model (e.g., Isolation Forests or ARIMA for time-series).
**Why:** True anomaly detection requires historical baseline data to calculate standard deviations or seasonality (e.g., knowing that a facility uses more heating oil in January than July). Without a historical dataset, a complex model would overfit or throw constant false positives. Simple bounds-checking was faster to implement and sufficient to demonstrate the Human-in-the-Loop review UI.

## 3. Dedicated Database Migrations for Multi-Tenancy (Row-Level Security)
**What was omitted:** Multi-tenancy is handled via standard Django ORM `ForeignKey` relationships to a `Client` model, rather than strict Postgres Row-Level Security (RLS) or separate database schemas per tenant.
**Why:** Implementing schema-based multi-tenancy (using packages like `django-tenants`) severely complicates database migrations and local testing. For a prototype, logical isolation via ORM filtering proves the concept. Before scaling to highly regulated enterprise clients, migrating to true RLS at the database level would provide stronger data leak guarantees.
