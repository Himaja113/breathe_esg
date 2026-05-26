# Data Model Architecture

The data model for Breathe ESG was designed to serve as a robust foundation for a multi-tenant enterprise carbon accounting platform. The priority is ensuring strict auditability, data integrity across diverse ingestion sources, and seamless normalization.

## 1. Multi-Tenancy (`clients` app)
**Implementation:** A central `Client` model acts as the root tenant. The `User` model is extended from Django's `AbstractUser` to include a `ForeignKey` to `Client`. 
**Why:** Enterprise SaaS platforms require strict data isolation. By tying every subsequent record (Ingestion Jobs, Normalized Records, Audit Logs) to a `Client`, we can enforce tenant isolation at the ORM query level, ensuring Client A never sees Client B's data, even if they share the same database.

## 2. Source-of-Truth Tracking (`ingestion` app)
**Implementation:** The `IngestionJob` model tracks the raw file upload, status, and processing timestamp.
**Why:** We must never lose the raw data. The `NormalizedRecord` model stores the parsed data, but it includes a `JSONField` called `raw_data` containing the exact unadulterated row from the original file, along with an `ingestion_job` ForeignKey linking it back to the exact file upload. If an auditor questions a number, we can trace it back to the exact row in the exact file provided by the client.

## 3. Scope 1/2/3 Categorization & Unit Normalization (`normalization` app)
**Implementation:** The `EmissionFactor` model serves as the master reference data (e.g., EPA or DEFRA factors). The `NormalizedRecord` processes incoming data, standardizes the unit (e.g., converting distance to `km` or fuel to `L`), and links to the appropriate `EmissionFactor`.
**Why:** Carbon accounting requires mapping diverse activities to standard Scopes. By separating the `EmissionFactor` into its own reference table, we decouple the raw activity (driving a car) from the math used to calculate emissions. The `NormalizedRecord` stores the generic `activity_type`, standardizes the `normalized_quantity`, and calculates the `calculated_emissions_kg` using the related factor. It inherently inherits the Scope (1, 2, or 3) from the Emission Factor.

## 4. Immutable Audit Trail (`audit` app)
**Implementation:** Every time a `NormalizedRecord` is created, updated, or approved, a signal/view creates an `AuditLog` entry. The `AuditLog` stores the user who made the change, a timestamp, a reason, and a complete snapshot of the `before_state` and `after_state` as JSON.
**Why:** Financial and ESG auditors require an immutable history of data tampering. If a human analyst manually alters a quantity from 100 to 150 because of a typo in the raw data, the platform must prove who made the change and what the original value was. The `AuditLog` provides this exact compliance requirement.
