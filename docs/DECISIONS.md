# Design Decisions & Ambiguities Resolved (25% Weight)

During the rapid 4-day architecture phase, several major ambiguities required decisive resolution. The overarching philosophy was: **Favor defensible, robust workflows over fragile feature bloat.**

## 1. Ambiguity: Ingestion via Flat-Files vs. Direct API Integration
* **Decision:** We built file upload parsers for all three sources instead of attempting OData/REST API integrations.
* **Why:** The prompt mentioned SAP, Utility portals, and Concur. In the real world, enterprise IT departments take 3-6 months to provision API keys and firewall exceptions for SAP middleware (like PO/PI) or Concur. Building an MVP assuming direct API access is fundamentally unrealistic. Flat-file exports (ALV grids for SAP, CSV dumps for Utilities) are the lowest common denominator and the absolute reality of ESG onboarding.

## 2. Ambiguity: German SAP Column Headers
* **Decision:** We explicitly mapped only the quantitative fields and ignored the organizational metadata.
* **Why:** German SAP abbreviations are a known integration pain point. Attempting to ingest the entire ALV grid would bloat the `JSONField` with irrelevant hierarchy data.
* **Mapping Logic Used in Parser:**
  * `MENGE` $\rightarrow$ `quantity` (The core consumption number)
  * `MEINS` $\rightarrow$ `unit` (Required for unit normalization logic)
  * `BUDAT` $\rightarrow$ `date` (Posting date acts as our `reporting_date` anchor)
  * `WERKS` $\rightarrow$ `plant_code` (Useful for auditing the physical source)
  * `BKTXT` $\rightarrow$ `fuel_type` (Simulating the activity categorization)
  * **Ignored:** `MANDT` (Client), `BUKRS` (Company Code), `MATNR` (Material Number). These are enterprise organizational metadata that, while useful in an ERP, are irrelevant for raw mathematical emissions calculation in a prototype.

## 3. Ambiguity: Defining an "Anomaly" without Historical Data
* **Decision:** Implemented rigid heuristic bounds-checking (e.g., negative consumption, or quantities over 100,000) rather than a statistical ML model.
* **Why:** To do statistical anomaly detection (e.g., Isolation Forests), you need historical baselines to define a standard deviation. We are onboarding a *new* enterprise client. We have zero historical data. Attempting to build an ML model on day one would result in garbage outputs and false positives. Hard-coded heuristics guarantee we catch catastrophic typos (e.g., entering MWh instead of kWh) without over-engineering.

## 4. Ambiguity: The Analyst vs Auditor UX (10% Weight)
* **Decision:** The application defaults to a public, Read-Only "Auditor Mode". Mutations (Approving, Editing, Ingesting) require explicit Analyst Login via DRF Token Authentication.
* **Why:** Auditors are there to read the ledger and check the math. Giving them a UI where they could accidentally click "Approve" compromises the integrity of the audit. By forcing Analysts behind a strict Role-Based Access Control (RBAC) wall, we protect the data and guarantee that the `AuditLog` always captures a specific, authorized `User` rather than an anonymous session. The UX is clean, explicitly highlights flagged anomalies in red, and abstracts away JSON payloads unless requested.

## Questions for the PM
1. **Approval Workflows:** Does the client require multi-stage approvals? Currently, any Analyst can approve a flagged record. In a SOX-compliant environment, does a Junior Analyst need a Senior Manager's sign-off before it locks for audit?
2. **Emission Factor Versioning:** If the EPA retroactively updates a 2023 grid electricity factor, do we recalculate the locked ledger and trigger an audit event, or do we freeze the historical ledger permanently and only apply it forward?
