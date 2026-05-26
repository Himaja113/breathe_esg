# Data Model Architecture (35% Weight)

The data model is designed defensively. ESG data is notoriously messy, and auditors demand cryptographic-level proof of exactly where a number came from and who touched it. A traditional rigid relational schema fails here because ingestion formats change weekly. 

This model solves that via extreme decoupling and immutable snapshotting.

## 1. Multi-Tenancy (`Client` Model)
* **What:** Every single operational table (`User`, `IngestionJob`, `NormalizedRecord`) routes back to a single `Client` tenant.
* **Why:** ESG data is highly confidential. We cannot risk cross-tenant data bleed. Relying on application-level filtering without a strict foreign-key hierarchy is negligent. By anchoring everything to `Client`, Django's ORM `select_related` and `filter(client=X)` enforces logical isolation at the query compiler level.

## 2. The Ingestion Engine & Source-of-Truth (`IngestionJob` + `raw_data`)
* **What:** The `NormalizedRecord` model contains a `JSONField` called `raw_data`. This stores the exact, unadulterated dictionary parsed from the source file. It also contains an `ingestion_job` ForeignKey linking it to the exact file upload timestamp.
* **Why:** You cannot alter the source of truth. If a client disputes a carbon calculation 12 months from now, we must be able to prove *exactly* what they uploaded. If we only stored the parsed/normalized quantities, we destroy the original context. The `JSONField` survives all future schema migrations and provides an absolute audit anchor.

## 3. Decoupled Emission Factors (`EmissionFactor` Model)
* **What:** Activities (e.g., burning diesel) and their mathematical conversions (e.g., 2.68 kg CO2e per L) are strictly decoupled. The `NormalizedRecord` stores the activity, but uses a ForeignKey to `EmissionFactor` to calculate the final `calculated_emissions_kg`. 
* **Why:** Emission factors update constantly (e.g., the EPA publishes new grid electricity factors annually). If we hardcoded the math into the application logic, historical ledgers would corrupt upon update. By making `EmissionFactor` a standalone table with `valid_from` dates and `version` tracking, we lock the math to the specific reporting period. Furthermore, Scope 1/2/3 categorization is bound to the *Factor*, not the *Record*, ensuring consistent downstream reporting.

## 4. Immutable Audit Trail (`AuditLog` Model)
* **What:** The `AuditLog` table intercepts all state mutations (via `perform_update` in the DRF viewset). It logs the `user`, a `timestamp`, the `reason`, and a full JSON snapshot of both `before_state` and `after_state`.
* **Why:** Analysts must be able to clean data (e.g., fixing a typo from `1000` to `100`). But legally, we cannot simply overwrite the database row. The `AuditLog` guarantees non-repudiation. If an auditor asks why a row changed, the platform instantly surfaces the exact analyst, the exact timestamp, and the exact delta.
