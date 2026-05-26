# Data Sources & Ingestion Research (20% Weight)

To build a realistic engine, I researched the specific pain points of ingesting from three notoriously difficult enterprise silos.

## 1. SAP (Fuel & Procurement Data)
* **Research:** SAP offers modern APIs (OData) and legacy middleware (IDocs/BAPIs). However, ESG onboarding is usually driven by sustainability teams, not IT. Getting SAP PI/PO firewall exceptions takes months. Therefore, the reality of SAP ingestion is flat-file ALV grid exports or background job spool files.
* **Sample Data:** My `sap_procurement.txt` mimics a tab-delimited ALV export. It uses realistic SAP column headers: `MANDT` (Client), `WERKS` (Plant), `MENGE` (Quantity), `MEINS` (Unit of Measure), and `BUDAT` (Posting Date).
* **What would break in production:** I used `BKTXT` (Document Header Text) to simulate the fuel type (e.g., "Diesel"). In reality, SAP uses Material Numbers (`MATNR`). A production deployment would instantly break without a master mapping table linking `MATNR: 100045` to the `EmissionFactor: Diesel`.

## 2. Utility Portals (Electricity Data)
* **Research:** Utilities provide data via PDFs, portal CSVs, or Green Button XML. OCR on PDFs is too brittle. Green Button is standard but not universally adopted. The lowest common denominator is the portal CSV export.
* **Sample Data:** My `utility_data.csv` avoids the trap of assigning consumption to a calendar month. Utility bills cover "billing periods" (e.g., Jan 14 to Feb 12). The sample explicitly defines `billing_period_start` and `billing_period_end`. 
* **What would break in production:** The prototype assumes the data is final. In the real world, utilities frequently issue "estimated" meter reads and then send a true-up correction file two months later. Without logic to handle negative consumption adjustments or supersede previous records, we would double-count carbon.

## 3. Corporate Travel (Concur / Navan)
* **Research:** Travel platforms have rich APIs, but the data shape is deeply fragmented. A flight emits based on distance and cabin class (business class takes up more floor space). A hotel emits based on room nights and country-specific grid factors. 
* **Sample Data:** My `travel_data.csv` uses a `segment_type` column (`flight`, `hotel`, `car`) to route normalization logic. The ingestor dynamically checks the segment type to know whether it should look for `distance_km` or `nights`.
* **What would break in production:** The prototype lumps all flights into a single emission factor. Real deployments must parse the origin and destination airport codes (e.g., `JFK-LHR`) to calculate the exact haul distance, as short-haul flights have drastically different emission curves than long-haul flights.
