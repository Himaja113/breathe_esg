# Data Sources & Ingestion Research

Breathe ESG handles three primary enterprise data sources. Each requires specific parsing logic to extract the normalized fields required for carbon accounting.

## 1. SAP (Fuel & Procurement Data)
**Format Researched:** Standard SAP ERP text exports (often tab-delimited or ALV grid dumps).
**What I Learned:** SAP uses internal German abbreviations for column headers (`MANDT` for Client, `WERKS` for Plant, `MENGE` for Quantity, `MEINS` for Unit of Measure, `BUDAT` for Posting Date). These files are notoriously rigid and rely on internal material codes (`MATNR`).
**Sample Data:** Our sample `sap_procurement.txt` is a tab-delimited file mimicking this exact structure. We specifically parse `MENGE`, `MEINS`, and `BUDAT` to get the core activity data, and we use a generic `BKTXT` (Document Header Text) column to simulate the fuel type (e.g., "Diesel") for simplicity.
**What would break in production:** In a real deployment, relying on `BKTXT` for the fuel type would break instantly. Real SAP deployments use `MATNR` (Material Numbers). We would need to build a complex mapping table that links specific SAP Material Numbers (e.g., `MAT100045`) to an Emission Factor (`Diesel`).

## 2. Utility Portals (Electricity Data)
**Format Researched:** Standard CSV exports from major utility providers (e.g., PG&E, ConEdison) or aggregated facility management software.
**What I Learned:** Utility bills span a "billing period" rather than a single day. They report consumption in Kilowatt-hours (`kWh`) or Megawatt-hours (`MWh`) alongside financial cost.
**Sample Data:** Our sample `utility_data.csv` includes `billing_period_start`, `billing_period_end`, and `consumption_kwh`. We use the `billing_period_end` as the official `reporting_date` for carbon ledgers.
**What would break in production:** Real utility data frequently contains estimated meter reads followed by corrections in the next month. This prototype assumes all data is final. In production, we would need logic to handle negative consumption adjustments or handle overlapping billing periods to prevent double-counting emissions.

## 3. Corporate Travel (Business Travel Data)
**Format Researched:** Exports from corporate travel platforms like Concur, Egencia, or Navan.
**What I Learned:** Travel data is heavily fragmented. Flights are measured in distance (km/miles), hotels are measured in room nights, and rental cars are measured in distance or fuel cost.
**Sample Data:** Our sample `travel_data.csv` accommodates this fragmentation by including a `segment_type` column (`flight`, `hotel`, `car`). The ingestion logic uses conditional statements to route the normalization process (e.g., looking for `distance_km` if it's a flight, but looking for `nights` if it's a hotel).
**What would break in production:** Flight emissions vary drastically based on cabin class (Economy vs. First Class) due to the footprint area of the seat, and whether it's short-haul vs. long-haul. Our prototype maps all flights to a generic "Flight" emission factor. In production, the engine would need to parse the `cabin_class`, `origin`, and `destination` airports to calculate accurate haul distances and apply specific IPCC emission factors.
