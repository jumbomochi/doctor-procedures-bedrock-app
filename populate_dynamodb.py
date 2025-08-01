#!/usr/bin/env python3

"""
DynamoDB Data Population Script for Doctor Procedures
Creates substantial test data with realistic medical procedures and costs
"""

import json
import boto3
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration
TABLE_NAME = 'DoctorProcedures'
REGION = 'us-east-1'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# Sample data pools
DOCTORS = [
    'Sarah Johnson', 'Michael Chen', 'Emily Rodriguez', 'James Wilson',
    'Lisa Thompson', 'David Kim', 'Rachel Green', 'Mark Davis',
    'Jennifer Lee', 'Robert Brown', 'Amanda Martinez', 'Christopher Taylor',
    'Michelle White', 'Andrew Garcia', 'Nicole Anderson', 'Kevin Thomas'
]

# Medical procedure codes with base costs and variations
PROCEDURES = {
    'CONS001': {
        'name': 'Initial Consultation',
        'base_cost': 250,
        'variation': 0.3  # 30% cost variation
    },
    'CONS002': {
        'name': 'Follow-up Consultation',
        'base_cost': 180,
        'variation': 0.25
    },
    'XRAY001': {
        'name': 'Chest X-Ray',
        'base_cost': 150,
        'variation': 0.2
    },
    'XRAY002': {
        'name': 'Abdominal X-Ray',
        'base_cost': 175,
        'variation': 0.2
    },
    'LAB001': {
        'name': 'Complete Blood Count',
        'base_cost': 85,
        'variation': 0.15
    },
    'LAB002': {
        'name': 'Lipid Panel',
        'base_cost': 120,
        'variation': 0.2
    },
    'LAB003': {
        'name': 'Thyroid Function Test',
        'base_cost': 95,
        'variation': 0.18
    },
    'SURG001': {
        'name': 'Minor Surgery - Lesion Removal',
        'base_cost': 800,
        'variation': 0.4
    },
    'SURG002': {
        'name': 'Arthroscopic Knee Surgery',
        'base_cost': 3500,
        'variation': 0.5
    },
    'CARD001': {
        'name': 'Electrocardiogram (ECG)',
        'base_cost': 200,
        'variation': 0.25
    },
    'CARD002': {
        'name': 'Echocardiogram',
        'base_cost': 450,
        'variation': 0.3
    },
    'ENDO001': {
        'name': 'Colonoscopy',
        'base_cost': 1200,
        'variation': 0.35
    },
    'ENDO002': {
        'name': 'Upper Endoscopy',
        'base_cost': 950,
        'variation': 0.3
    },
    'PHYS001': {
        'name': 'Physical Therapy Session',
        'base_cost': 120,
        'variation': 0.2
    },
    'PHYS002': {
        'name': 'Occupational Therapy',
        'base_cost': 135,
        'variation': 0.22
    },
    'RAD001': {
        'name': 'MRI Scan - Brain',
        'base_cost': 2200,
        'variation': 0.4
    },
    'RAD002': {
        'name': 'CT Scan - Abdomen',
        'base_cost': 1500,
        'variation': 0.35
    },
    'DERM001': {
        'name': 'Skin Biopsy',
        'base_cost': 350,
        'variation': 0.3
    },
    'DERM002': {
        'name': 'Mole Removal',
        'base_cost': 275,
        'variation': 0.25
    },
    'VACC001': {
        'name': 'Annual Flu Vaccination',
        'base_cost': 45,
        'variation': 0.15
    }
}

def generate_cost(base_cost, variation):
    """Generate a realistic cost with variation"""
    min_cost = base_cost * (1 - variation)
    max_cost = base_cost * (1 + variation)
    cost = random.uniform(min_cost, max_cost)
    return round(cost, 2)

def generate_timestamp():
    """Generate a random timestamp within the last 2 years"""
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now()
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_date = start_date + timedelta(days=random_days)
    
    # Add random hours and minutes
    random_hours = random.randint(8, 17)  # Business hours
    random_minutes = random.choice([0, 15, 30, 45])  # 15-minute intervals
    random_date = random_date.replace(hour=random_hours, minute=random_minutes, second=0, microsecond=0)
    
    return random_date.isoformat()

def create_entry(doctor_name, procedure_code, procedure_info):
    """Create a single DynamoDB entry"""
    cost = generate_cost(procedure_info['base_cost'], procedure_info['variation'])
    timestamp = generate_timestamp()
    
    return {
        'DoctorName': doctor_name,  # Hash key
        'ProcedureTime': timestamp,  # Range key
        'procedure_code': procedure_code,
        'procedure_name': procedure_info['name'],
        'cost': Decimal(str(cost)),
        'time_logged': timestamp
    }

def populate_database():
    """Populate the database with substantial test data"""
    entries = []
    
    print("🏥 Generating comprehensive medical procedure data...")
    
    # Ensure each doctor has at least 5 entries for some procedures
    priority_procedures = ['CONS001', 'CONS002', 'LAB001', 'XRAY001', 'PHYS001']
    
    # Generate guaranteed entries (each doctor gets 5 entries for priority procedures)
    for doctor in DOCTORS:
        for proc_code in priority_procedures:
            proc_info = PROCEDURES[proc_code]
            for _ in range(5):
                entry = create_entry(doctor, proc_code, proc_info)
                entries.append(entry)
                print(f"✓ {doctor} - {proc_code} (${entry['cost']})")
    
    print(f"\n📊 Generated {len(entries)} priority entries")
    
    # Generate additional random entries to reach substantial data
    target_additional = 200  # Additional entries beyond the priority ones
    procedure_codes = list(PROCEDURES.keys())
    
    for _ in range(target_additional):
        doctor = random.choice(DOCTORS)
        proc_code = random.choice(procedure_codes)
        proc_info = PROCEDURES[proc_code]
        
        entry = create_entry(doctor, proc_code, proc_info)
        entries.append(entry)
        
        if len(entries) % 50 == 0:
            print(f"📈 Generated {len(entries)} total entries...")
    
    print(f"\n🎯 Total entries to insert: {len(entries)}")
    print("\n🔄 Starting batch insertion to DynamoDB...")
    
    # Batch insert to DynamoDB
    batch_size = 25  # DynamoDB batch write limit
    success_count = 0
    
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        
        try:
            with table.batch_writer() as batch_writer:
                for entry in batch:
                    batch_writer.put_item(Item=entry)
            
            success_count += len(batch)
            print(f"✅ Inserted batch {i//batch_size + 1}: {success_count}/{len(entries)} entries")
            
        except Exception as e:
            print(f"❌ Error inserting batch {i//batch_size + 1}: {str(e)}")
            continue
    
    print(f"\n🎉 Database population complete!")
    print(f"📊 Successfully inserted {success_count} entries")
    
    # Generate summary statistics
    generate_summary()

def generate_summary():
    """Generate and display summary statistics"""
    print(f"\n📈 Data Summary:")
    print(f"👨‍⚕️ Doctors: {len(DOCTORS)}")
    print(f"🏥 Procedure Types: {len(PROCEDURES)}")
    print(f"💰 Cost Range: ${min(p['base_cost'] * (1-p['variation']) for p in PROCEDURES.values()):.2f} - ${max(p['base_cost'] * (1+p['variation']) for p in PROCEDURES.values()):.2f}")
    
    print(f"\n🔍 Sample Procedures:")
    for code, info in list(PROCEDURES.items())[:5]:
        min_cost = info['base_cost'] * (1 - info['variation'])
        max_cost = info['base_cost'] * (1 + info['variation'])
        print(f"  {code}: {info['name']} (${min_cost:.2f} - ${max_cost:.2f})")
    
    print(f"\n📋 Test Scenarios Created:")
    print(f"  ✓ Each doctor has 5+ entries for common procedures")
    print(f"  ✓ Same procedure codes with different costs")
    print(f"  ✓ Realistic medical procedure names and codes")
    print(f"  ✓ Historical timestamps over 2 years")
    print(f"  ✓ Cost variations reflecting real-world pricing")

if __name__ == "__main__":
    print("🚀 Starting DynamoDB data population...")
    print(f"📍 Target table: {TABLE_NAME}")
    print(f"🌍 Region: {REGION}")
    
    try:
        populate_database()
        print(f"\n✅ Script completed successfully!")
        print(f"🧪 Your database is now ready for comprehensive testing!")
        
    except Exception as e:
        print(f"\n❌ Error during population: {str(e)}")
        print(f"💡 Make sure:")
        print(f"   - AWS credentials are configured")
        print(f"   - DynamoDB table '{TABLE_NAME}' exists")
        print(f"   - You have write permissions to the table")
