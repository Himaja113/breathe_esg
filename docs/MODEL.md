# Data Model Architecture (35% Weight)

The data model is designed defensively. ESG data is notoriously messy, and auditors demand cryptographic-level proof of exactly where a number came from and who touched it. This model solves that via extreme decoupling, immutable snapshotting, and strict normalization chains.

## 1. Multi-Tenancy & Core Schema (`Client` & `NormalizedRecord`)
* **What:** Every single operational table routes back to a single `Client` tenant. `NormalizedRecord` acts as the unified ledger for all ESG activities.
* **Why:** ESG data is highly confidential. By anchoring everything to `Client`, Django's ORM enforces logical isolation at the query compiler level.

### `NormalizedRecord` Schema
```python
class NormalizedRecord(models.Model):
    client          = models.ForeignKey(Client)
    raw_record      = models.OneToOneField(RawRecord) # Link to exact ingestion job & parsed row
    
    # Categorization
    scope           = models.CharField(choices=['SCOPE_1', 'SCOPE_2', 'SCOPE_3'])
    category        = models.CharField()  # e.g., "Stationary Combustion"
    source_type     = models.CharField()  # e.g., "SAP", "UTILITY", "TRAVEL"
    activity_type   = models.CharField()  # e.g., "Diesel", "Electricity", "Flight"
    
    # Unit Normalization Chain
    original_quantity = models.DecimalField()
    original_unit   = models.CharField()
    normalized_quantity = models.DecimalField() # Converted to SI base units (L, m3, kWh, km)
    normalized_unit = models.CharField()
    
    # Accounting & Math
    reporting_date  = models.DateField()
    emission_factor = models.ForeignKey(EmissionFactor, null=True)
    calculated_emissions_kg = models.DecimalField(null=True)
    
    # State & Audit
    status          = models.CharField(choices=['PENDING', 'FLAGGED', 'APPROVED', 'LOCKED'])
    anomaly_reason  = models.TextField(null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
```

## 2. Unit Normalization Logic
To ensure emission calculations are mathematically sound, quantities are rigorously normalized before an `EmissionFactor` is applied. 
* **The Chain:** `raw unit -> SI base unit -> kg CO2e`
* **Example:** If SAP exports Natural Gas in `m³` but the emission factor uses `GJ` or `kWh`, the ingestion parser intercepts the `original_unit` (e.g. `m³`) and performs a volumetric-to-energy conversion (e.g., $1 \text{ m}^3 \approx 10.55 \text{ kWh}$) to store the `normalized_quantity` in `kWh`. The `EmissionFactor` is then cleanly applied to the SI base unit.

## 3. Handling Billing Periods
Utility data rarely aligns with a calendar month (e.g., Jan 14 to Feb 12). 
* **How it is handled:** The data model relies on `reporting_date` as the strict accounting anchor for the ledger. For utility true-ups or multi-month bills, the ingestion layer calculates the median date of the `billing_period_start` and `billing_period_end` and assigns it to `reporting_date`. 
* **Tradeoff:** This is a simplification for the prototype. In production, `NormalizedRecord` would require explicit `period_start` and `period_end` DateFields, and the analytical engine would prorate consumption linearly across calendar days to satisfy strict greenhouse gas (GHG) protocol monthly reporting.

## 4. The Ingestion Engine & Source-of-Truth
### `IngestionJob` and `RawRecord` Schema
```python
class IngestionJob(models.Model):
    client       = models.ForeignKey(Client)
    source_type  = models.CharField(choices=['SAP', 'UTILITY', 'TRAVEL'])
    file_ref     = models.CharField()
    status       = models.CharField(choices=['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'])
    ingested_at  = models.DateTimeField(auto_now_add=True)

class RawRecord(models.Model):
    job          = models.ForeignKey(IngestionJob)
    row_index    = models.IntegerField()
    raw_data     = models.JSONField() # The exact, unadulterated dictionary parsed from the source file
```
* **Why:** You cannot alter the source of truth. If a client disputes a carbon calculation 12 months from now, we must prove *exactly* what they uploaded. The `JSONField` survives all future schema migrations and provides an absolute audit anchor without sacrificing relational querying capabilities on the `NormalizedRecord` side. The `status` on `IngestionJob` ensures the analyst UX can accurately reflect batch progress.

## 5. Decoupled Emission Factors (`EmissionFactor` Model)
```python
class EmissionFactor(models.Model):
    substance    = models.CharField() # e.g., "Diesel", "Grid Electricity"
    scope        = models.CharField(choices=['SCOPE_1', 'SCOPE_2', 'SCOPE_3'])
    factor_value = models.DecimalField() # e.g., 2.68
    unit         = models.CharField() # e.g., "L", "kWh"
    source       = models.CharField() # e.g., "EPA", "DEFRA"
    version      = models.CharField() # e.g., "2024"
    valid_from   = models.DateField()
```
* **Why:** Activities and their mathematical conversions are strictly decoupled. If we hardcoded the math into the application logic, historical ledgers would corrupt upon an EPA factor update. Scope categorization is securely bound to the *Factor*, not arbitrary user input.

## 6. Immutable Audit Trail (`AuditLog` vs `ReviewEvent`)
We maintain two distinct logs to satisfy different compliance domains:
1. **`ReviewEvent` (Workflow Tracking):**
   * Tracks standard business actions: Approved, Flagged, Rejected.
   * *Schema snippet:* `record_id`, `user_id`, `action`, `note`, `timestamp`
2. **`AuditLog` (Cryptographic State Tracking):**
   * Intercepts all state mutations (via `perform_update`). Logs the exact delta.
   * *Schema snippet:* `record_id`, `user_id`, `before_state (JSON)`, `after_state (JSON)`, `reason`, `timestamp`
* **Why:** `ReviewEvent` drives the UI timeline. `AuditLog` guarantees non-repudiation. If an auditor asks why a row changed, we instantly surface the exact analyst, the timestamp, and the exact before/after JSON delta.
