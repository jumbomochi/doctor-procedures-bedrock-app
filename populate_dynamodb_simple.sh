#!/bin/bash

# DynamoDB Data Population Script using AWS CLI
# Creates substantial test data for the doctor procedures table

set -e

TABLE_NAME="DoctorProcedures"
REGION="us-east-1"
DATA_FILE="sample_data.json"

echo "🏥 Creating substantial test data for DynamoDB..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Generate JSON data file
cat > $DATA_FILE << 'EOF'
[
  {"doctor_name": "Dr. Sarah Johnson", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 275.50, "timestamp": "2024-01-15T09:30:00"},
  {"doctor_name": "Dr. Sarah Johnson", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 250.00, "timestamp": "2024-02-20T10:15:00"},
  {"doctor_name": "Dr. Sarah Johnson", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 290.25, "timestamp": "2024-03-10T14:00:00"},
  {"doctor_name": "Dr. Sarah Johnson", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 265.75, "timestamp": "2024-04-05T11:45:00"},
  {"doctor_name": "Dr. Sarah Johnson", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 255.00, "timestamp": "2024-05-12T16:30:00"},
  
  {"doctor_name": "Dr. Michael Chen", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 240.00, "timestamp": "2024-01-20T08:30:00"},
  {"doctor_name": "Dr. Michael Chen", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 280.50, "timestamp": "2024-02-15T13:15:00"},
  {"doctor_name": "Dr. Michael Chen", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 270.25, "timestamp": "2024-03-22T09:00:00"},
  {"doctor_name": "Dr. Michael Chen", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 245.75, "timestamp": "2024-04-18T15:45:00"},
  {"doctor_name": "Dr. Michael Chen", "procedure_code": "CONS001", "procedure_name": "Initial Consultation", "cost": 295.00, "timestamp": "2024-05-25T10:30:00"},
  
  {"doctor_name": "Dr. Emily Rodriguez", "procedure_code": "LAB001", "procedure_name": "Complete Blood Count", "cost": 85.00, "timestamp": "2024-01-10T09:00:00"},
  {"doctor_name": "Dr. Emily Rodriguez", "procedure_code": "LAB001", "procedure_name": "Complete Blood Count", "cost": 92.50, "timestamp": "2024-01-25T11:30:00"},
  {"doctor_name": "Dr. Emily Rodriguez", "procedure_code": "LAB001", "procedure_name": "Complete Blood Count", "cost": 78.25, "timestamp": "2024-02-12T14:15:00"},
  {"doctor_name": "Dr. Emily Rodriguez", "procedure_code": "LAB001", "procedure_name": "Complete Blood Count", "cost": 88.75, "timestamp": "2024-03-05T10:45:00"},
  {"doctor_name": "Dr. Emily Rodriguez", "procedure_code": "LAB001", "procedure_name": "Complete Blood Count", "cost": 95.00, "timestamp": "2024-04-20T16:00:00"},
  
  {"doctor_name": "Dr. James Wilson", "procedure_code": "XRAY001", "procedure_name": "Chest X-Ray", "cost": 150.00, "timestamp": "2024-01-08T10:30:00"},
  {"doctor_name": "Dr. James Wilson", "procedure_code": "XRAY001", "procedure_name": "Chest X-Ray", "cost": 165.50, "timestamp": "2024-02-14T13:45:00"},
  {"doctor_name": "Dr. James Wilson", "procedure_code": "XRAY001", "procedure_name": "Chest X-Ray", "cost": 142.25, "timestamp": "2024-03-18T09:15:00"},
  {"doctor_name": "Dr. James Wilson", "procedure_code": "XRAY001", "procedure_name": "Chest X-Ray", "cost": 158.75, "timestamp": "2024-04-22T11:00:00"},
  {"doctor_name": "Dr. James Wilson", "procedure_code": "XRAY001", "procedure_name": "Chest X-Ray", "cost": 172.00, "timestamp": "2024-05-30T15:30:00"},
  
  {"doctor_name": "Dr. Lisa Thompson", "procedure_code": "SURG001", "procedure_name": "Minor Surgery - Lesion Removal", "cost": 800.00, "timestamp": "2024-01-12T08:00:00"},
  {"doctor_name": "Dr. Lisa Thompson", "procedure_code": "SURG001", "procedure_name": "Minor Surgery - Lesion Removal", "cost": 750.50, "timestamp": "2024-02-28T10:30:00"},
  {"doctor_name": "Dr. Lisa Thompson", "procedure_code": "SURG001", "procedure_name": "Minor Surgery - Lesion Removal", "cost": 925.25, "timestamp": "2024-03-15T14:45:00"},
  {"doctor_name": "Dr. Lisa Thompson", "procedure_code": "SURG001", "procedure_name": "Minor Surgery - Lesion Removal", "cost": 675.00, "timestamp": "2024-04-10T11:15:00"},
  {"doctor_name": "Dr. Lisa Thompson", "procedure_code": "SURG001", "procedure_name": "Minor Surgery - Lesion Removal", "cost": 850.75, "timestamp": "2024-05-18T16:00:00"},

  {"doctor_name": "Dr. David Kim", "procedure_code": "CARD001", "procedure_name": "Electrocardiogram (ECG)", "cost": 200.00, "timestamp": "2024-01-22T09:30:00"},
  {"doctor_name": "Dr. David Kim", "procedure_code": "CARD001", "procedure_name": "Electrocardiogram (ECG)", "cost": 185.50, "timestamp": "2024-02-18T12:00:00"},
  {"doctor_name": "Dr. David Kim", "procedure_code": "CARD001", "procedure_name": "Electrocardiogram (ECG)", "cost": 220.25, "timestamp": "2024-03-25T15:15:00"},
  {"doctor_name": "Dr. David Kim", "procedure_code": "CARD001", "procedure_name": "Electrocardiogram (ECG)", "cost": 195.75, "timestamp": "2024-04-30T10:45:00"},
  {"doctor_name": "Dr. David Kim", "procedure_code": "CARD001", "procedure_name": "Electrocardiogram (ECG)", "cost": 235.00, "timestamp": "2024-05-22T14:30:00"},

  {"doctor_name": "Dr. Rachel Green", "procedure_code": "LAB002", "procedure_name": "Lipid Panel", "cost": 120.00, "timestamp": "2024-01-16T08:45:00"},
  {"doctor_name": "Dr. Rachel Green", "procedure_code": "LAB002", "procedure_name": "Lipid Panel", "cost": 135.25, "timestamp": "2024-02-22T11:30:00"},
  {"doctor_name": "Dr. Rachel Green", "procedure_code": "LAB002", "procedure_name": "Lipid Panel", "cost": 108.50, "timestamp": "2024-03-20T13:15:00"},
  {"doctor_name": "Dr. Rachel Green", "procedure_code": "LAB002", "procedure_name": "Lipid Panel", "cost": 142.75, "timestamp": "2024-04-15T16:45:00"},
  {"doctor_name": "Dr. Rachel Green", "procedure_code": "LAB002", "procedure_name": "Lipid Panel", "cost": 125.00, "timestamp": "2024-05-28T09:00:00"},

  {"doctor_name": "Dr. Mark Davis", "procedure_code": "PHYS001", "procedure_name": "Physical Therapy Session", "cost": 120.00, "timestamp": "2024-01-09T10:00:00"},
  {"doctor_name": "Dr. Mark Davis", "procedure_code": "PHYS001", "procedure_name": "Physical Therapy Session", "cost": 135.50, "timestamp": "2024-01-23T14:30:00"},
  {"doctor_name": "Dr. Mark Davis", "procedure_code": "PHYS001", "procedure_name": "Physical Therapy Session", "cost": 115.25, "timestamp": "2024-02-06T11:15:00"},
  {"doctor_name": "Dr. Mark Davis", "procedure_code": "PHYS001", "procedure_name": "Physical Therapy Session", "cost": 128.75, "timestamp": "2024-02-20T15:45:00"},
  {"doctor_name": "Dr. Mark Davis", "procedure_code": "PHYS001", "procedure_name": "Physical Therapy Session", "cost": 140.00, "timestamp": "2024-03-12T09:30:00"},

  {"doctor_name": "Dr. Jennifer Lee", "procedure_code": "RAD001", "procedure_name": "MRI Scan - Brain", "cost": 2200.00, "timestamp": "2024-01-30T08:00:00"},
  {"doctor_name": "Dr. Jennifer Lee", "procedure_code": "RAD001", "procedure_name": "MRI Scan - Brain", "cost": 2450.50, "timestamp": "2024-02-25T10:30:00"},
  {"doctor_name": "Dr. Jennifer Lee", "procedure_code": "RAD001", "procedure_name": "MRI Scan - Brain", "cost": 1975.25, "timestamp": "2024-03-30T13:45:00"},
  {"doctor_name": "Dr. Jennifer Lee", "procedure_code": "RAD001", "procedure_name": "MRI Scan - Brain", "cost": 2350.00, "timestamp": "2024-04-25T15:00:00"},
  {"doctor_name": "Dr. Jennifer Lee", "procedure_code": "RAD001", "procedure_name": "MRI Scan - Brain", "cost": 2125.75, "timestamp": "2024-05-20T11:30:00"},

  {"doctor_name": "Dr. Robert Brown", "procedure_code": "ENDO001", "procedure_name": "Colonoscopy", "cost": 1200.00, "timestamp": "2024-01-18T07:30:00"},
  {"doctor_name": "Dr. Robert Brown", "procedure_code": "ENDO001", "procedure_name": "Colonoscopy", "cost": 1350.25, "timestamp": "2024-02-16T09:45:00"},
  {"doctor_name": "Dr. Robert Brown", "procedure_code": "ENDO001", "procedure_name": "Colonoscopy", "cost": 1125.50, "timestamp": "2024-03-14T12:00:00"},
  {"doctor_name": "Dr. Robert Brown", "procedure_code": "ENDO001", "procedure_name": "Colonoscopy", "cost": 1285.75, "timestamp": "2024-04-12T14:15:00"},
  {"doctor_name": "Dr. Robert Brown", "procedure_code": "ENDO001", "procedure_name": "Colonoscopy", "cost": 1175.00, "timestamp": "2024-05-15T10:45:00"},

  {"doctor_name": "Dr. Amanda Martinez", "procedure_code": "DERM001", "procedure_name": "Skin Biopsy", "cost": 350.00, "timestamp": "2024-01-24T11:00:00"},
  {"doctor_name": "Dr. Amanda Martinez", "procedure_code": "DERM001", "procedure_name": "Skin Biopsy", "cost": 385.50, "timestamp": "2024-02-21T13:30:00"},
  {"doctor_name": "Dr. Amanda Martinez", "procedure_code": "DERM001", "procedure_name": "Skin Biopsy", "cost": 325.25, "timestamp": "2024-03-19T15:45:00"},
  {"doctor_name": "Dr. Amanda Martinez", "procedure_code": "DERM001", "procedure_name": "Skin Biopsy", "cost": 375.75, "timestamp": "2024-04-16T09:15:00"},
  {"doctor_name": "Dr. Amanda Martinez", "procedure_code": "DERM001", "procedure_name": "Skin Biopsy", "cost": 395.00, "timestamp": "2024-05-14T16:30:00"},

  {"doctor_name": "Dr. Christopher Taylor", "procedure_code": "CONS002", "procedure_name": "Follow-up Consultation", "cost": 180.00, "timestamp": "2024-01-11T10:30:00"},
  {"doctor_name": "Dr. Christopher Taylor", "procedure_code": "CONS002", "procedure_name": "Follow-up Consultation", "cost": 195.25, "timestamp": "2024-02-08T14:00:00"},
  {"doctor_name": "Dr. Christopher Taylor", "procedure_code": "CONS002", "procedure_name": "Follow-up Consultation", "cost": 165.50, "timestamp": "2024-03-07T11:45:00"},
  {"doctor_name": "Dr. Christopher Taylor", "procedure_code": "CONS002", "procedure_name": "Follow-up Consultation", "cost": 185.75, "timestamp": "2024-04-04T13:15:00"},
  {"doctor_name": "Dr. Christopher Taylor", "procedure_code": "CONS002", "procedure_name": "Follow-up Consultation", "cost": 202.00, "timestamp": "2024-05-02T15:30:00"}
]
EOF

echo "📊 Generated sample data with 50+ entries"
echo "🔄 Starting bulk insertion to DynamoDB..."

# Convert JSON to DynamoDB batch write format and insert
python3 << 'PYTHON_SCRIPT'
import json
import boto3
from decimal import Decimal

# Load the JSON data
with open('sample_data.json', 'r') as f:
    data = json.load(f)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('DoctorProcedures')

# Convert floats to Decimal for DynamoDB
for item in data:
    item['cost'] = Decimal(str(item['cost']))

# Batch write to DynamoDB
batch_size = 25
success_count = 0

for i in range(0, len(data), batch_size):
    batch = data[i:i + batch_size]
    
    try:
        with table.batch_writer() as batch_writer:
            for item in batch:
                batch_writer.put_item(Item=item)
        
        success_count += len(batch)
        print(f"✅ Inserted batch {i//batch_size + 1}: {success_count}/{len(data)} entries")
        
    except Exception as e:
        print(f"❌ Error inserting batch {i//batch_size + 1}: {str(e)}")

print(f"\n🎉 Successfully inserted {success_count} entries!")
PYTHON_SCRIPT

# Clean up
rm $DATA_FILE

echo ""
echo "✅ Database population complete!"
echo "📊 Data Summary:"
echo "   - 10+ Doctors with realistic names"
echo "   - 10+ Different procedure codes"
echo "   - Each doctor has 5+ entries for common procedures"
echo "   - Cost variations for same procedure codes"
echo "   - Timestamps spread across multiple months"
echo ""
echo "🧪 Test scenarios you can now try:"
echo "   1. 'Show history for Dr. Sarah Johnson'"
echo "   2. 'What is the cost for procedure CONS001?'"
echo "   3. 'Add a new procedure for Dr. Test Doctor'"
echo "   4. Check cost variations for same procedures"
echo ""
echo "🚀 Your DynamoDB table is now ready for comprehensive testing!"
