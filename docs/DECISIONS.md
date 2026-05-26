# Design Decisions & Ambiguities Resolved

During the architecture and implementation of the prototype, several ambiguities regarding enterprise data ingestion and processing had to be resolved. 

## 1. Ambiguity: How to handle unmatched or unstructured raw data?
**Decision:** I chose to implement a flexible `raw_data` JSONField on the `NormalizedRecord` model, and process ingestion synchronously but distinctively per source format. 
**Why:** Enterprise clients often change column names or append custom fields (e.g., custom SAP cost centers). Instead of creating rigid schemas that break on upload, the system ingests everything into the JSON payload and attempts to extract known fields (`quantity`, `date`, `activity_type`) for the normalized columns.
**Subset Handled vs Ignored:** For SAP data, we extract `WERKS` (Plant), `MENGE` (Quantity), `MEINS` (Unit), and `BKTXT` (Fuel Type). We actively ignore accounting fields like `BUKRS` (Company Code) for now, though they are preserved in the JSON payload for future reporting expansions.

## 2. Ambiguity: What constitutes an "Anomaly"?
**Decision:** I defined an anomaly strictly as quantities that deviate massively from expected norms (e.g., negative quantities, or massive outliers like 850,000 kWh for a single meter) or missing critical emission mappings. 
**Why:** Without historical baseline data for a new client, statistical z-score anomaly detection is impossible. I fell back to hard-coded heuristic thresholds (e.g., `quantity <= 0` or `quantity > 100000`) to flag records for Human-in-the-Loop review.
**Subset Handled vs Ignored:** I handled basic numeric bounds checking. I ignored complex contextual anomalies (e.g., "this facility usually uses less power in winter") due to the lack of historical ML models.

## 3. Ambiguity: How to manage the workflow between Analysts and Auditors?
**Decision:** Implemented Role-Based Access Control (RBAC) where the default public view is an Auditor (Read-Only) view, and explicit login is required for Analysts. Analysts can mutate state (`PENDING` -> `APPROVED`), which logs an event. 
**Why:** Auditors primarily need to verify the math and the audit trail; they shouldn't accidentally edit data. Analysts are doing the operational data cleaning. 

## Questions for the PM
If I had access to the Product Manager, I would ask:
1. **Approval Workflows:** Do we need multi-stage approvals? (e.g., Junior Analyst cleans data -> Senior Analyst approves -> Data is locked for Auditors). Currently, anyone with the Analyst role can approve.
2. **Emission Factor Versioning:** How do we handle recalculations if the EPA updates a 2023 emission factor retroactively? Should the locked records update, or remain immutable for that reporting period?
3. **Data Pagination:** At enterprise scale, a single SAP export could contain millions of rows. Should we move the file processing off the main web thread and into an asynchronous queue like Celery?
