# DynamoDB Data Population Guide

## 🎯 Overview
This guide provides scripts to populate your DynamoDB table with substantial test data for comprehensive testing of the Doctor Procedures application.

## 📊 Test Data Features

### **Data Volume:**
- **50+ entries** across multiple doctors and procedures
- **10+ doctors** with realistic medical professional names
- **10+ procedure codes** covering various medical specialties

### **Key Testing Scenarios:**
✅ **Same procedure, different costs**: Each doctor has 5+ entries for common procedures with cost variations  
✅ **Realistic medical procedures**: Consultations, lab tests, imaging, surgeries, therapy sessions  
✅ **Cost variations**: 15-50% price differences reflecting real-world medical pricing  
✅ **Historical data**: Timestamps spread across multiple months  
✅ **Comprehensive coverage**: Data supports all app features (add, quote, history)

## 🚀 Quick Start (Recommended)

### **Option 1: Simple Script (No extra dependencies)**
```bash
# Run the simple population script
./populate_dynamodb_simple.sh
```

### **Option 2: Advanced Script (Requires boto3)**
```bash
# Install Python dependencies
pip install -r requirements-data.txt

# Run the comprehensive script
python3 populate_dynamodb.py
```

## 📋 Prerequisites

### **AWS Configuration:**
```bash
# Configure AWS credentials
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Output format: json
```

### **Verify Table Exists:**
```bash
# Check if your DynamoDB table exists
aws dynamodb describe-table --table-name doctor-procedures-table --region us-east-1
```

## 📈 Sample Data Structure

### **Doctors Included:**
- Dr. Sarah Johnson
- Dr. Michael Chen  
- Dr. Emily Rodriguez
- Dr. James Wilson
- Dr. Lisa Thompson
- Dr. David Kim
- Dr. Rachel Green
- Dr. Mark Davis
- Dr. Jennifer Lee
- Dr. Robert Brown
- And more...

### **Procedure Codes:**
- **CONS001**: Initial Consultation ($175-$325)
- **CONS002**: Follow-up Consultation ($135-$225)
- **LAB001**: Complete Blood Count ($70-$100)
- **XRAY001**: Chest X-Ray ($120-$180)
- **SURG001**: Minor Surgery ($480-$1,200)
- **CARD001**: Electrocardiogram ($150-$250)
- **RAD001**: MRI Scan ($1,300-$3,100)
- **ENDO001**: Colonoscopy ($780-$1,620)
- And more medical procedures...

## 🧪 Testing Scenarios

After population, you can test these scenarios:

### **1. History Queries:**
```
"Show history for Dr. Sarah Johnson"
"What procedures has Dr. Michael Chen performed?"
```

### **2. Cost Queries:**
```
"What is the cost for procedure CONS001?"
"Show me prices for Complete Blood Count"
```

### **3. Cost Variations:**
- Same procedure code (e.g., CONS001) will show different costs
- Realistic price ranges based on doctor, location, complexity

### **4. Add New Procedures:**
```
"Add a procedure for Dr. Test Doctor"
Procedure Code: TEST001
Name: Test Procedure  
Cost: 500.00
```

## 🔍 Data Verification

### **Check Data via AWS CLI:**
```bash
# Scan table to see all entries
aws dynamodb scan --table-name doctor-procedures-table --region us-east-1

# Count total entries
aws dynamodb scan --table-name doctor-procedures-table --region us-east-1 --select COUNT

# Query specific doctor
aws dynamodb query --table-name doctor-procedures-table --region us-east-1 \
  --key-condition-expression "doctor_name = :doctor" \
  --expression-attribute-values '{":doctor":{"S":"Dr. Sarah Johnson"}}'
```

### **Test via React App:**
1. Open your React app (localhost:3000 or S3 URL)
2. Try chat queries: "Show history for Dr. Sarah Johnson"
3. Use Quick Actions to get quotes for existing procedures
4. Add new procedures and verify they appear

## 📊 Expected Results

### **History Queries:**
- **Dr. Sarah Johnson** should show 5+ entries for CONS001 with different costs
- Each doctor should have multiple procedure entries
- Timestamps should show realistic scheduling patterns

### **Cost Quotes:**
- **CONS001** should show multiple cost options from different doctors
- Costs should vary realistically (e.g., $250-$295 for consultations)

### **Add Procedure:**
- Should successfully add new entries to existing doctors
- New procedure codes should be accepted

## 🛠 Troubleshooting

### **Common Issues:**

1. **AWS Credentials Error**
   ```bash
   # Reconfigure AWS
   aws configure
   # Verify credentials
   aws sts get-caller-identity
   ```

2. **Table Not Found**
   ```bash
   # Check table exists
   aws dynamodb list-tables --region us-east-1
   # Deploy your SAM application if missing
   sam deploy --guided
   ```

3. **Permission Denied**
   - Ensure your AWS user has DynamoDB write permissions
   - Check IAM policies include `dynamodb:PutItem` and `dynamodb:BatchWriteItem`

4. **Script Fails**
   ```bash
   # Check Python version
   python3 --version
   # Install dependencies
   pip install boto3
   ```

## 🔄 Updating Data

### **Clear Existing Data:**
```bash
# Truncate table (be careful!)
aws dynamodb scan --table-name doctor-procedures-table --region us-east-1 \
  --attributes-to-get "doctor_name,procedure_code" \
  --query "Items[*].[doctor_name.S,procedure_code.S]" --output text | \
  while read doctor procedure; do
    aws dynamodb delete-item --table-name doctor-procedures-table --region us-east-1 \
      --key "{\"doctor_name\":{\"S\":\"$doctor\"},\"procedure_code\":{\"S\":\"$procedure\"}}"
  done
```

### **Re-populate:**
```bash
# Run population script again
./populate_dynamodb_simple.sh
```

## 💡 Tips for Testing

1. **Start with history queries** to verify data loaded correctly
2. **Test cost variations** by querying the same procedure code multiple times
3. **Add new procedures** to verify write functionality works
4. **Use different doctor names** to test the full dataset
5. **Try edge cases** like non-existent procedures or doctors

Your DynamoDB table should now have comprehensive test data ready for thorough application testing!
