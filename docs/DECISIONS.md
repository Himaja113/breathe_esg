# Architectural & Product Decisions

## 1. SAP Data: Flat File Export vs. Live OData API
**Decision:** Accept SAP flat-file/IDoc exports (tab-delimited) rather than building a live OData API integration.
**Reasoning:** In the enterprise ERP space, granting direct live API access to third-party SaaS vendors is a massive security hurdle requiring months of InfoSec review. However, setting up a scheduled background job in SAP to drop a flat file to an SFTP or S3 bucket is standard practice and highly accepted.

## 2. Utility Data: CSV over PDF Parsing
**Decision:** Require utility data to be uploaded via the provider's CSV export portal.
**Reasoning:** While PDF scraping (via OCR or text extraction) seems magical, utility bill templates change frequently without notice. A minor layout change breaks the parser. CSV exports from portals (like PG&E or Con Ed) maintain a much stricter schema contract.

## 3. Corporate Travel: Concur CSV vs Navan API
**Decision:** Default to standard expense management CSV exports (like SAP Concur).
**Reasoning:** Similar to the SAP decision, integrating with modern APIs (like Navan) requires OAuth enterprise setups which elongate the onboarding process. A CSV upload works on day one.

## 4. Billing Periods vs. Calendar Months
**Decision:** Record the `reporting_date` as the `billing_period_end`. 
**Reasoning:** Apportioning a utility bill across calendar months (e.g., splitting a Mar 15 - Apr 15 bill) requires complex assumptions about daily usage curves (weekdays vs weekends). For carbon accounting prototypes, logging the emissions in the month the bill ends is a widely accepted simplification.

## 5. German SAP Headers Mapping
**Decision:** Map standard SAP German abbreviations directly in the parser.
**Reasoning:** SAP exports standard field names (MANDT, BUKRS, WERKS, MATNR, MENGE, MEINS). Translating these in the backend logic keeps the frontend clean for the analyst. `WERKS` (Plant) is mapped to validate locations, `MENGE` (Quantity) and `MEINS` (Base Unit of Measure) are extracted for normalization.
