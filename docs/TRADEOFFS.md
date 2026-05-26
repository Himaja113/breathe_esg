# Engineering Tradeoffs (10% Weight)

To deliver a sharp, highly reliable core engine in 4 days, I aggressively scoped out features that would introduce fragility without proving the core value proposition. Here are three things deliberately omitted and why:

## 1. Asynchronous Task Queues (No Celery/Redis)
**What was omitted:** The file ingestion engine currently parses files synchronously within the Django HTTP request/response cycle.
**Why:** A true enterprise platform processing a 500MB SAP export must offload parsing to a background worker (like Celery) to prevent gateway timeouts. However, adding Redis and Celery introduces massive infrastructure overhead and deployment complexity. For a prototype proving data normalization logic on sample sets <10MB, synchronous processing is a calculated technical debt. The parsing logic itself is isolated in `ingestion/parsers.py` and can be easily wrapped in a `@shared_task` later.

## 2. Machine Learning for Anomaly Detection
**What was omitted:** I did not implement Isolation Forests, ARIMA, or any statistical ML models for catching suspicious records, relying instead on hard-coded heuristics.
**Why:** Adding `scikit-learn` or time-series forecasting looks great on a resume but fails miserably in production without historical baselines. We are onboarding a *new* client. We don't know if their factory spikes electricity usage in July vs January. Any ML model deployed on day one would overfit or generate endless false positives, ruining the Analyst UX. Simple bounds-checking (e.g., `quantity <= 0`) is honest, deterministic, and immediately valuable.

## 3. Database-Level Row-Level Security (RLS)
**What was omitted:** I did not configure strict PostgreSQL Row-Level Security policies or separate schema-per-tenant structures (e.g., using `django-tenants`). 
**Why:** Schema-based multi-tenancy makes database migrations incredibly complex and brittle during rapid prototyping. While it provides the ultimate guarantee against cross-tenant data leaks, Django's ORM is robust enough for an MVP. By anchoring all models to a `Client` ForeignKey, we enforce logical multi-tenancy at the application layer. This allowed me to iterate on the schema 10x faster without fighting Postgres schema routing.
