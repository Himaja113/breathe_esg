# Data Sources & Ingestion Research (20% Weight)

To build a realistic engine, I researched the specific pain points of ingesting from three notoriously difficult enterprise silos.

## 1. SAP (Fuel & Procurement Data)
* **Research:** SAP offers modern APIs (OData) and legacy middleware (IDocs/BAPIs). However, ESG onboarding is usually driven by sustainability teams, not IT. Getting SAP PI/PO firewall exceptions takes months. Therefore, the reality of SAP ingestion is flat-file ALV grid exports or background job spool files.
* **Sample Data:** My `sap_procurement.txt` mimics a tab-delimited ALV export. It has 50 rows across 3 plants (`IN01`, `IN02`, `DE03`), covering diesel, petrol, and natural gas procurement in Q2 2026. Units are intentionally mixed (`L` and `m³`). Row 47 has a zero quantity (`MENGE=0`) to test the anomaly detection heuristics. The `BKTXT` column maps to fuel type as a deliberate simplification.
* **What would break in production:** I used `BKTXT` (Document Header Text) to simulate the fuel type (e.g., "Diesel"). In reality, SAP uses Material Numbers (`MATNR`). A production deployment would instantly break without a master mapping table linking `MATNR: 100045` to the `EmissionFactor: Diesel`.

## 2. Utility Portals (Electricity Data)
* **Research:** Utilities provide data via PDFs, portal CSVs, or Green Button XML. OCR on PDFs is too brittle. Green Button is standard but not universally adopted. The lowest common denominator is the portal CSV export.
* **Sample Data:** My `utility_data.csv` avoids the trap of assigning consumption to a single calendar month. Utility bills cover "billing periods" (e.g., Jan 14 to Feb 12). The sample explicitly defines `billing_period_start` and `billing_period_end` across 20 rows of electricity and water meter readings. The dataset deliberately includes massive consumption spikes (e.g. `100,000 kWh`) to trigger the anomaly flagging system.
* **What would break in production:** The prototype assumes the data is final. In the real world, utilities frequently issue "estimated" meter reads and then send a true-up correction file two months later. Without logic to handle negative consumption adjustments or supersede previous records, we would double-count carbon.

## 3. Corporate Travel (Concur / Navan)
* **Research:** Travel platforms have rich APIs, but the data shape is deeply fragmented. A flight emits based on distance and cabin class (business class takes up more floor space). A hotel emits based on room nights and country-specific grid factors. 
* **Sample Data:** My `travel_data.csv` contains 30 rows of employee travel. It uses a `segment_type` column (`flight`, `hotel`, `car`) to route normalization logic. The dataset includes raw distances (`distance_km`) for flights, room nights (`nights`) for hotels, and fuel quantities for rental cars. 
* **What would break in production:** The prototype lumps all flights into a single emission factor based purely on distance. Real deployments must parse the exact origin and destination airport codes (e.g., `JFK-LHR`) to calculate the exact haul distance, as short-haul flights have drastically different emission curves than long-haul flights. Additionally, cabin classes (Economy vs. First) would need to be ingested to accurately calculate per-passenger footprint.
