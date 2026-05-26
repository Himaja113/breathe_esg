# Tradeoffs & Omissions

To maintain focus and deliver a sharp, defensible prototype, the following features were deliberately omitted:

## 1. Automated Real-Time API Integrations
-   **Omission:** No live webhooks or API pulls from external systems (SAP, Navan, Utility Providers).
-   **Reasoning:** We chose a file-upload architecture. Enterprise onboarding is heavily gated by InfoSec. A platform that can operate initially via secure file uploads can onboard clients in weeks rather than months. We traded "real-time magic" for realistic enterprise adoption speed.

## 2. Automated Live Emission Factor Updates
-   **Omission:** The platform does not continuously poll EPA or DEFRA APIs for the latest emission factors.
-   **Reasoning:** In carbon accounting, audit stability is paramount. If a 2022 emissions report is audited in 2023, the calculation must use the exact emission factors active at that time. We chose a static, versioned `EmissionFactor` table. Analysts explicitly assign/update versions rather than the system silently changing the math underneath them.

## 3. Multi-Currency Procurement Normalization (Spend-based methods)
-   **Omission:** We handle physical activity data (liters, kWh, km) but deferred spend-based emission calculations (e.g., $1000 spent on concrete = X kg CO2e).
-   **Reasoning:** Spend-based calculations require complex FX rate normalization across dates and regions, plus inflation adjustments. This adds massive complexity without fundamentally changing the core architecture of the carbon ledger. We prioritized activity-based data (which is more accurate for Scopes 1 & 2 anyway) for the prototype.
