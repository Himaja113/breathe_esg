# Data Sources & Formats

## 1. SAP Fuel & Procurement (Flat File)
-   **Format Spec Assumed:** Standard SAP ABAP report export (tab-delimited `.txt`).
-   **Surprises:** SAP often exports dates in `DD.MM.YYYY` format and uses German abbreviations for columns (e.g., `BUDAT` for Posting Date, `MEINS` for unit).
-   **Fragility:** If a client uses custom Z-fields in their SAP implementation or exports as a spool file instead of a strict tab-delimited file, the parser will break. 

## 2. Utility Data (Electricity)
-   **Format Spec Assumed:** Standard utility portal CSV download.
-   **Surprises:** Meters sometimes report in MWh instead of kWh depending on the industrial scale of the facility, often without explicit column headers (just a tariff code change).
-   **Sample Data:** Our sample generator explicitly creates a massive consumption row (850,000) to trigger the anomaly detection, mimicking an MWh masquerading as kWh.
-   **Fragility:** Different utilities use wildly different column names for `consumption_kwh` vs `Usage` vs `Billed_Qty`. A production system requires a mapping engine layer before ingestion.

## 3. Corporate Travel
-   **Format Spec Assumed:** Concur Expense Standard Extract (CSV).
-   **Surprises:** Travel records often contain IATA codes (JFK, LHR) but lack actual distances. Real-world systems require a geographic library (like `geopy`) to calculate great-circle distances between airports. 
-   **Sample Data:** We generate mixed flights, hotels, and cars. We omit distances on flights to simulate the need for IATA lookups (though the prototype flags this as an anomaly rather than performing the live Haversine calculation to avoid external API dependencies).
-   **Fragility:** If expense systems aggregate multi-leg flights into a single line item, distance calculations and cabin class emission factors become highly inaccurate.
