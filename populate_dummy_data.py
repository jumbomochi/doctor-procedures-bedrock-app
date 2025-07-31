#!/usr/bin/env python3
"""
populate_dummy_data.py - Populate DynamoDB with dummy data for testing
"""
import json
import boto3
import os
from datetime import datetime, timezone

def create_dynamodb_table():
    """Create DynamoDB table locally"""
    try:
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        
        table = dynamodb.create_table(
            TableName='DoctorProcedures',
            KeySchema=[
                {'AttributeName': 'DoctorName', 'KeyType': 'HASH'},
                {'AttributeName': 'ProcedureTime', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'DoctorName', 'AttributeType': 'S'},
                {'AttributeName': 'ProcedureTime', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        print("✅ DynamoDB table 'DoctorProcedures' created successfully")
        return table
        
    except Exception as e:
        if 'ResourceInUseException' in str(e):
            print("ℹ️ Table already exists, using existing table")
            return dynamodb.Table('DoctorProcedures')
        else:
            print(f"❌ Error creating table: {e}")
            return None

def populate_dummy_data():
    """Populate the table with dummy data"""
    try:
        # Use local DynamoDB endpoint for testing
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        table = dynamodb.Table('DoctorProcedures')
        
        # Load dummy data
        with open('doctor_procedures_table/dummy_data.json', 'r') as f:
            dummy_data = json.load(f)
        
        # Insert dummy data
        with table.batch_writer() as batch:
            for item in dummy_data:
                batch.put_item(Item=item)
        
        print(f"✅ Successfully inserted {len(dummy_data)} dummy records")
        
        # Verify data
        response = table.scan()
        print(f"📊 Total items in table: {response['Count']}")
        
    except Exception as e:
        print(f"❌ Error populating dummy data: {e}")

if __name__ == "__main__":
    print("🗄️ Setting up DynamoDB with dummy data...")
    
    # Check if DynamoDB Local is running
    try:
        dynamodb = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
        dynamodb.list_tables()
        print("✅ DynamoDB Local is running")
    except Exception as e:
        print("❌ DynamoDB Local is not running. Please start it first:")
        print("   docker run -p 8000:8000 amazon/dynamodb-local")
        exit(1)
    
    # Create table and populate data
    table = create_dynamodb_table()
    if table:
        populate_dummy_data()
    else:
        print("❌ Failed to create or access table")
        exit(1)
