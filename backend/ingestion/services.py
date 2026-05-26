import csv
import json
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from django.utils import timezone
from ingestion.models import IngestionJob, RawRecord
from normalization.models import NormalizedRecord, EmissionFactor

def parse_date(date_str: str) -> datetime.date:
    try:
        if '.' in date_str:
            return datetime.strptime(date_str, '%d.%m.%Y').date()
        elif '-' in date_str:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            return datetime.strptime(date_str, '%Y%m%d').date()
    except ValueError:
        return timezone.now().date()

def process_sap_row(row: Dict[str, Any], job: IngestionJob, client) -> Tuple[NormalizedRecord, str]:
    # SAP columns: MANDT, BUKRS, WERKS, MATNR, MENGE, MEINS, BLDAT, BUDAT, BKTXT
    date_str = row.get('BUDAT') or row.get('BLDAT') or timezone.now().strftime('%Y-%m-%d')
    reporting_date = parse_date(date_str)
    
    original_qty_str = row.get('MENGE', '0').strip()
    original_qty = Decimal(original_qty_str) if original_qty_str else Decimal('0')
    
    original_unit = row.get('MEINS', '').strip().upper()
    
    # Normalize units to m3 for Scope 1 fuels
    normalized_qty = original_qty
    normalized_unit = 'm3'
    if original_unit == 'L':
        normalized_qty = original_qty / Decimal('1000')
    elif original_unit == 'GAL':
        normalized_qty = original_qty * Decimal('0.00378541')
    elif original_unit in ['M3', 'M³']:
        pass
    else:
        normalized_unit = original_unit # Keep as is if unknown
        
    activity_type = row.get('BKTXT', 'Unknown Fuel')
    
    anomaly = []
    if normalized_qty <= 0:
        anomaly.append("Quantity is zero or negative.")
    if reporting_date > timezone.now().date():
        anomaly.append("Reporting date is in the future.")
    if row.get('WERKS', '').strip() not in ['IN01', 'IN02', 'DE03']:
        anomaly.append(f"Unknown plant code: {row.get('WERKS')}.")
        
    status = NormalizedRecord.Status.FLAGGED if anomaly else NormalizedRecord.Status.PENDING
    
    raw_record = RawRecord.objects.create(job=job, raw_data=row)
    
    norm_rec = NormalizedRecord(
        client=client,
        raw_record=raw_record,
        scope=EmissionFactor.Scope.SCOPE_1,
        category='Stationary Combustion',
        source_type='SAP',
        reporting_date=reporting_date,
        activity_type=activity_type,
        original_quantity=original_qty,
        original_unit=original_unit,
        normalized_quantity=normalized_qty,
        normalized_unit=normalized_unit,
        status=status,
        anomaly_reason=" ".join(anomaly)
    )
    return norm_rec

def process_utility_row(row: Dict[str, Any], job: IngestionJob, client) -> Tuple[NormalizedRecord, str]:
    # Utility columns: account_number, meter_id, service_address, billing_period_start, billing_period_end, consumption_kwh, demand_kw, tariff_code, total_charges
    reporting_date = parse_date(row.get('billing_period_end', timezone.now().strftime('%Y-%m-%d')))
    
    qty_str = row.get('consumption_kwh', '0').strip()
    original_qty = Decimal(qty_str) if qty_str else Decimal('0')
    
    # Detect if it's MWh by checking if it's unexpectedly low (heuristic) or if a unit column exists
    # For prototype, assume it might just be marked in tariff_code or anomaly detection based on size
    original_unit = 'kWh'
    normalized_qty = original_qty
    normalized_unit = 'kWh'
    
    anomaly = []
    if normalized_qty <= 0:
        anomaly.append("Quantity is zero or negative.")
    if normalized_qty > 500000: # Heuristic for anomaly
        anomaly.append(f"Unusually high consumption ({normalized_qty} kWh) - verify if this is MWh.")
        
    status = NormalizedRecord.Status.FLAGGED if anomaly else NormalizedRecord.Status.PENDING
    
    raw_record = RawRecord.objects.create(job=job, raw_data=row)
    
    norm_rec = NormalizedRecord(
        client=client,
        raw_record=raw_record,
        scope=EmissionFactor.Scope.SCOPE_2,
        category='Purchased Electricity',
        source_type='UTILITY',
        reporting_date=reporting_date,
        activity_type='Grid Electricity',
        original_quantity=original_qty,
        original_unit=original_unit,
        normalized_quantity=normalized_qty,
        normalized_unit=normalized_unit,
        status=status,
        anomaly_reason=" ".join(anomaly)
    )
    return norm_rec

def process_travel_row(row: Dict[str, Any], job: IngestionJob, client) -> Tuple[NormalizedRecord, str]:
    # Travel columns: trip_id, traveler_id, segment_type, origin, destination, travel_date, cabin_class, hotel_name, hotel_city, nights, transport_mode, distance_km
    reporting_date = parse_date(row.get('travel_date', timezone.now().strftime('%Y-%m-%d')))
    
    segment_type = row.get('segment_type', '').strip().lower()
    activity_type = segment_type.capitalize()
    
    original_qty = Decimal('0')
    original_unit = ''
    normalized_qty = Decimal('0')
    normalized_unit = ''
    anomaly = []
    
    if segment_type == 'flight' or segment_type == 'car':
        dist_str = row.get('distance_km', '0').strip()
        original_qty = Decimal(dist_str) if dist_str else Decimal('0')
        original_unit = 'km'
        normalized_qty = original_qty
        normalized_unit = 'km'
        
        if not row.get('origin') or not row.get('destination'):
            anomaly.append("Missing origin or destination.")
        if normalized_qty <= 0:
            anomaly.append("Distance is missing or zero. Need to derive from IATA codes.")
    elif segment_type == 'hotel':
        nights_str = row.get('nights', '0').strip()
        original_qty = Decimal(nights_str) if nights_str else Decimal('0')
        original_unit = 'nights'
        normalized_qty = original_qty
        normalized_unit = 'nights'
    else:
        anomaly.append(f"Unknown segment type: {segment_type}")
        
    status = NormalizedRecord.Status.FLAGGED if anomaly else NormalizedRecord.Status.PENDING
    
    raw_record = RawRecord.objects.create(job=job, raw_data=row)
    
    norm_rec = NormalizedRecord(
        client=client,
        raw_record=raw_record,
        scope=EmissionFactor.Scope.SCOPE_3,
        category='Business Travel (Cat 6)',
        source_type='TRAVEL',
        reporting_date=reporting_date,
        activity_type=activity_type,
        original_quantity=original_qty,
        original_unit=original_unit,
        normalized_quantity=normalized_qty,
        normalized_unit=normalized_unit,
        status=status,
        anomaly_reason=" ".join(anomaly)
    )
    return norm_rec

def process_file(job: IngestionJob, client, file_content: str):
    job.status = IngestionJob.Status.PROCESSING
    job.save()
    
    records_to_create = []
    try:
        if job.source_type == IngestionJob.SourceType.SAP:
            reader = csv.DictReader(file_content.splitlines(), delimiter='\t')
            for row in reader:
                if any(row.values()): # Skip empty rows
                    norm_rec = process_sap_row(row, job, client)
                    records_to_create.append(norm_rec)
        elif job.source_type == IngestionJob.SourceType.UTILITY:
            reader = csv.DictReader(file_content.splitlines())
            for row in reader:
                if any(row.values()):
                    norm_rec = process_utility_row(row, job, client)
                    records_to_create.append(norm_rec)
        elif job.source_type == IngestionJob.SourceType.TRAVEL:
            reader = csv.DictReader(file_content.splitlines())
            for row in reader:
                if any(row.values()):
                    norm_rec = process_travel_row(row, job, client)
                    records_to_create.append(norm_rec)
                    
        # Calculate Emissions if a factor matches
        factors = list(EmissionFactor.objects.all())
        for rec in records_to_create:
            # Simple matching logic for prototype
            matched_factor = next((f for f in factors if f.scope == rec.scope and (rec.activity_type.lower() in f.substance.lower() or f.substance.lower() in rec.activity_type.lower())), None)
            if matched_factor:
                rec.emission_factor = matched_factor
                rec.calculated_emissions_kg = rec.normalized_quantity * matched_factor.factor_value
            elif not rec.anomaly_reason:
                rec.anomaly_reason = "Emission factor not found for the activity type."
                rec.status = NormalizedRecord.Status.FLAGGED
            
        NormalizedRecord.objects.bulk_create(records_to_create)
        
        job.row_count = len(records_to_create)
        job.error_count = sum(1 for r in records_to_create if r.status == NormalizedRecord.Status.FLAGGED)
        job.status = IngestionJob.Status.COMPLETED
    except Exception as e:
        job.status = IngestionJob.Status.FAILED
        job.error_count = 1
        # Log error in real app
    finally:
        job.save()
