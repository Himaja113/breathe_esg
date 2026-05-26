# Data Model Architecture

The data model for Breathe ESG is designed to ensure strict multi-tenancy, immutable auditability, and clear separation between raw ingested data and normalized operational data.

## Core Principles

1.  **Row-Level Multi-Tenancy**: Every operational record (`IngestionJob`, `NormalizedRecord`) has a foreign key to `Client`. We enforce this at the application layer via ORM filtering (e.g., in ViewSets) rather than schema-level multi-tenancy (like PostgreSQL schemas) because it reduces migration complexity, connection pooling overhead, and scales better for thousands of small-to-medium enterprise tenants.
2.  **Immutability of Source Truth**: The `RawRecord` model stores the exact JSON payload received during ingestion. It is never edited. This guarantees we can always trace a normalized value back to its origin file and re-run normalization if logic changes.
3.  **Append-Only Audit Trail**: The `AuditLog` table tracks every mutation on a `NormalizedRecord`. It records the `before_state` and `after_state` as JSON, along with the user and timestamp. This satisfies strict financial/ESG auditor requirements where manual adjustments must be fully traceable.

## Models Overview

### `clients.Client` & `clients.User`
-   **Client**: The tenant entity.
-   **User**: Custom Django user model with a role (`ADMIN`, `ANALYST`, `AUDITOR`) tied to a specific `Client`.

### `ingestion.IngestionJob` & `ingestion.RawRecord`
-   **IngestionJob**: Tracks a file upload event. Has statuses (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).
-   **RawRecord**: Linked to a job. Contains a `raw_data` JSONField holding the exact parsed row (e.g., SAP IDoc line or CSV row).

### `normalization.EmissionFactor`
-   Stores versioned emission factors (e.g., EPA 2023, DEFRA 2023). 
-   **Versioning Strategy**: Factors are stored as static rows with a `valid_from` date and a `version` string. They are applied at review time (or ingestion time as a cached calculation) so that historical records aren't retroactively altered if a new factor is released unless explicitly triggered.

### `normalization.NormalizedRecord`
-   The core operational table. One-to-one mapping with `RawRecord`.
-   **Unit Normalization**: Stores both the `original_quantity` (e.g., 500 GAL) and the `normalized_quantity` (converted to SI base units, e.g., 1.89 m³).
-   **Scope Tagging**: Explicitly tagged with GHG Protocol scopes (1, 2, or 3) and categories.
-   **Review State**: Uses a state machine (`PENDING` -> `FLAGGED` -> `APPROVED` -> `LOCKED`).

### `review.ReviewEvent` & `audit.AuditLog`
-   **ReviewEvent**: High-level semantic logging of analyst actions (e.g., "Approved by Alice", "Flagged by Bob").
-   **AuditLog**: Low-level field mutation logging. Triggered in the `perform_update` hook of the DRF ViewSet.
