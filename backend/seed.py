import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from clients.models import Client, User
from normalization.models import EmissionFactor

def create_emission_factors():
    factors = [
        ("Diesel", "SCOPE_1", "2.68", "L", "EPA", "2023"),
        ("Petrol", "SCOPE_1", "2.31", "L", "EPA", "2023"),
        ("Natural Gas", "SCOPE_1", "2.02", "m3", "EPA", "2023"),
        ("Grid Electricity", "SCOPE_2", "0.45", "kWh", "IPCC", "2023"),
        ("Flight", "SCOPE_3", "0.15", "km", "DEFRA", "2023"),
        ("Car", "SCOPE_3", "0.19", "km", "DEFRA", "2023"),
        ("Hotel", "SCOPE_3", "14.5", "nights", "DEFRA", "2023"),
    ]
    for sub, scope, val, unit, src, ver in factors:
        EmissionFactor.objects.get_or_create(
            substance=sub,
            scope=scope,
            defaults={
                'factor_value': val,
                'unit': unit,
                'source': src,
                'version': ver,
                'valid_from': '2023-01-01'
            }
        )
    print("Created Emission Factors")

def run():
    client, created = Client.objects.get_or_create(name="Breathe ESG Demo")
    if created:
        print("Created Demo Client")
        
    user, created = User.objects.get_or_create(username="analyst", defaults={
        'email': 'analyst@breatheesg.com',
        'role': User.Role.ANALYST,
        'client': client
    })
    if created:
        user.set_password("esg2024!")
        user.save()
        print("Created analyst user (password: esg2024!)")

    create_emission_factors()
    
    # Generate sample files in sample_data/
    os.makedirs('../sample_data', exist_ok=True)
    
    # 1. SAP Data
    with open('../sample_data/sap_procurement.txt', 'w') as f:
        f.write("MANDT\tBUKRS\tWERKS\tMATNR\tMENGE\tMEINS\tBLDAT\tBUDAT\tBKTXT\n")
        plants = ['IN01', 'IN02', 'DE03', 'UNKNOWN']
        fuels = [('Diesel', 'L'), ('Petrol', 'L'), ('Natural Gas', 'm3')]
        for i in range(50):
            plant = random.choice(plants) if i < 48 else 'UNKNOWN'
            fuel, unit = random.choice(fuels)
            qty = random.randint(100, 5000)
            if i == 45: qty = 0 # Anomaly
            date_str = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%d.%m.%Y')
            if i == 46: date_str = (datetime.now() + timedelta(days=5)).strftime('%d.%m.%Y') # Future date
            
            f.write(f"100\t1000\t{plant}\tMAT{i}\t{qty}\t{unit}\t{date_str}\t{date_str}\t{fuel}\n")
            
    # 2. Utility Data
    with open('../sample_data/utility_data.csv', 'w') as f:
        f.write("account_number,meter_id,service_address,billing_period_start,billing_period_end,consumption_kwh,demand_kw,tariff_code,total_charges\n")
        for i in range(30):
            start = datetime.now() - timedelta(days=30 + i*5)
            end = start + timedelta(days=30)
            qty = random.randint(1000, 15000)
            if i == 15: qty = 850000 # MWh masquerading as kWh anomaly
            f.write(f"ACC{i%3},METER{i%5},Address {i%2},{start.strftime('%Y-%m-%d')},{end.strftime('%Y-%m-%d')},{qty},50.5,TAR1,{(qty*0.12):.2f}\n")
            
    # 3. Travel Data
    with open('../sample_data/travel_data.csv', 'w') as f:
        f.write("trip_id,traveler_id,segment_type,origin,destination,travel_date,cabin_class,hotel_name,hotel_city,nights,transport_mode,distance_km\n")
        types = ['flight', 'hotel', 'car']
        for i in range(40):
            typ = random.choice(types)
            date_str = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            if typ == 'flight':
                dist = random.randint(500, 8000)
                if i == 5: dist = 0 # Anomaly
                f.write(f"TRIP{i},EMP{i%10},flight,JFK,LHR,{date_str},Economy,,,,,{dist}\n")
            elif typ == 'hotel':
                nights = random.randint(1, 5)
                f.write(f"TRIP{i},EMP{i%10},hotel,,,{date_str},,Hilton,London,{nights},,\n")
            else:
                dist = random.randint(50, 500)
                f.write(f"TRIP{i},EMP{i%10},car,LHR,Office,{date_str},,,,,Rental,{dist}\n")
                
    print("Generated sample data files in sample_data/")

if __name__ == '__main__':
    run()
