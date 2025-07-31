#!/usr/bin/env python3
"""
Script to populate the local DynamoDB table with dummy data for testing
"""
import json
import boto3
from boto3.dynamodb.conditions import Key

def populate_table():
    # Connect to local DynamoDB
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    table_name = 'DoctorProcedures'
    
    try:
        table = dynamodb.Table(table_name)
        
        # Load dummy data
        with open('doctor_procedures_table/dummy_data.json', 'r') as f:
            dummy_data = json.load(f)
        
        # Insert each item
        for item in dummy_data:
            table.put_item(Item=item)
            print(f"Inserted: {item['DoctorName']} - {item['procedure_name']}")
        
        print(f"\nSuccessfully populated {len(dummy_data)} items into {table_name} table")
        
        # Verify the data
        print(f"\nVerifying data in table:")
        response = table.scan()
        print(f"Total items in table: {response['Count']}")
        
    except Exception as e:
        print(f"Error populating table: {e}")

if __name__ == "__main__":
    populate_table()
