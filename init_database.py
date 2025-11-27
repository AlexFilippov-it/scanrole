#!/usr/bin/env python3
"""
LinkedIn Jobs Scraper - Database Initialization Script
Инициализирует базу данных Supabase для хранения вакансий
"""

import os
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://ohxveapplmhyhdrkyrtq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9oeHZlYXBwbG1oeWhkcmt5cnRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxMTMyMzEsImV4cCI6MjA3OTY4OTIzMX0.Uu3V32_9-DXvF4DUJCrCx_NeKZHRwkHq5l8BcN36o4k"

def init_supabase_client() -> Client:
    """Initialize Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def execute_sql_file(client: Client, sql_file_path: str):
    """Execute SQL commands from file"""
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # Split SQL commands (basic splitting by semicolon)
        # Note: This is a simple approach. For complex SQL, consider using a proper SQL parser
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]

        for command in commands:
            if command:  # Skip empty commands
                print(f"Executing: {command[:50]}...")
                try:
                    # Use rpc to execute raw SQL
                    result = client.rpc('exec_sql', {'sql': command})
                    print("✓ Success"                except Exception as e:
                    print(f"✗ Failed: {e}")
                    print(f"Command was: {command}")

    except FileNotFoundError:
        print(f"Error: SQL file '{sql_file_path}' not found")
    except Exception as e:
        print(f"Error executing SQL file: {e}")

def test_database_connection(client: Client):
    """Test database connection by checking if tables exist"""
    try:
        # Try to select from a table that should exist
        response = client.table('jobs').select('*').limit(1).execute()
        print("✓ Database connection successful")
        print("✓ Tables appear to be accessible")
    except Exception as e:
        print(f"✗ Database connection issue: {e}")

def main():
    print("LinkedIn Jobs Scraper - Database Initialization")
    print("=" * 50)

    # Initialize Supabase client
    print("Initializing Supabase client...")
    supabase = init_supabase_client()
    print("✓ Supabase client initialized")

    # Test connection
    print("\nTesting database connection...")
    test_database_connection(supabase)

    # Execute SQL initialization
    sql_file = "create_linkedin_scraper_tables.sql"
    print(f"\nExecuting SQL file: {sql_file}")
    execute_sql_file(supabase, sql_file)

    print("\n" + "=" * 50)
    print("Database initialization completed!")
    print("\nNext steps:")
    print("1. Check your Supabase dashboard to verify tables were created")
    print("2. Run the scraper script to start collecting job data")
    print("3. Consider setting up authentication for user management")

if __name__ == "__main__":
    main()
