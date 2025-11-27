#!/usr/bin/env python3
"""
CSV to Supabase Loader
Загружает данные из CSV файла скрапера в базу данных Supabase
"""

import os
import pandas as pd
from supabase import create_client, Client
import re
from urllib.parse import urlparse

# Supabase configuration
SUPABASE_URL = "https://ohxveapplmhyhdrkyrtq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9oeHZlYXBwbG1oeWhkcmt5cnRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxMTMyMzEsImV4cCI6MjA3OTY4OTIzMX0.Uu3V32_9-DXvF4DUJCrCx_NeKZHRwkHq5l8BcN36o4k"

def init_supabase_client() -> Client:
    """Initialize Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def extract_linkedin_job_id(job_url: str) -> str:
    """Extract LinkedIn job ID from URL"""
    if not job_url or job_url == 'N/A':
        return None

    # Extract job ID from URL like: https://www.linkedin.com/jobs/view/software-engineer-1-at-intuit-4333562794
    match = re.search(r'-(\d+)$', job_url)
    if match:
        return match.group(1)
    return None

def clean_text(text):
    """Clean text data"""
    if pd.isna(text) or text == 'N/A':
        return None
    return str(text).strip()

def load_csv_to_supabase(csv_file_path: str, supabase: Client, search_query: str = None):
    """Load CSV data to Supabase"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from {csv_file_path}")

        # Extract search query from filename if not provided
        if not search_query:
            filename = os.path.basename(csv_file_path)
            # Extract from pattern: jobs_{country}_{search_term}.csv
            match = re.match(r'jobs_(\w+)_(.+)\.csv', filename)
            if match:
                search_query = match.group(2).replace('_', ' ')

        print(f"Search query: {search_query}")

        # Transform and load data
        saved_count = 0
        skipped_count = 0

        for _, row in df.iterrows():
            # Extract LinkedIn job ID
            linkedin_job_id = extract_linkedin_job_id(row.get('Job URL'))

            # Prepare job data
            job_data = {
                'linkedin_job_id': linkedin_job_id,
                'title': clean_text(row.get('Title')),
                'company': clean_text(row.get('Company')),
                'location': clean_text(row.get('Location')),
                'date_posted_text': clean_text(row.get('Date Posted')),
                'logo_url': clean_text(row.get('Logo URL')),
                'job_url': clean_text(row.get('Job URL')),
                'search_query': search_query
            }

            # Remove None values
            job_data = {k: v for k, v in job_data.items() if v is not None}

            # Skip if no essential data
            if not job_data.get('title') or not job_data.get('job_url'):
                print(f"Skipped row - missing essential data: {job_data.get('title', 'No title')}")
                skipped_count += 1
                continue

            try:
                # Insert into Supabase
                response = supabase.table('scraped_jobs').insert(job_data).execute()

                if hasattr(response, 'data') and response.data:
                    saved_count += 1
                    if saved_count % 10 == 0:  # Progress indicator
                        print(f"Saved {saved_count} jobs...")
                else:
                    print(f"Failed to save job: {response}")
                    print(f"Job data: {job_data}")

            except Exception as e:
                # Handle duplicate key errors gracefully
                if 'duplicate key value' in str(e):
                    print(f"Skipped duplicate: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
                    skipped_count += 1
                else:
                    print(f"Error saving job {job_data.get('title', 'Unknown')}: {e}")

        print(f"\nCompleted!")
        print(f"Saved: {saved_count} jobs")
        print(f"Skipped: {skipped_count} jobs")
        print(f"Total processed: {len(df)} jobs")

        return saved_count

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found")
        return 0
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return 0

def find_latest_csv(directory: str = ".") -> str:
    """Find the most recently created CSV file in directory"""
    try:
        csv_files = [f for f in os.listdir(directory) if f.startswith('jobs_') and f.endswith('.csv')]

        if not csv_files:
            return None

        # Sort by modification time (newest first)
        csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)

        return os.path.join(directory, csv_files[0])

    except Exception as e:
        print(f"Error finding CSV files: {e}")
        return None

def main():
    print("CSV to Supabase Loader")
    print("=" * 40)

    # Initialize Supabase
    supabase = init_supabase_client()
    print("Supabase client initialized")

    # Find the latest CSV file or use command line argument
    import sys

    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = find_latest_csv()

    if not csv_file:
        print("No CSV file found. Usage: python csv_to_supabase.py [csv_file_path]")
        print("Or ensure CSV files starting with 'jobs_' exist in current directory")
        return

    print(f"Processing file: {csv_file}")

    # Load data to Supabase
    saved_count = load_csv_to_supabase(csv_file, supabase)

    if saved_count > 0:
        print(f"\nSuccessfully loaded {saved_count} jobs to Supabase!")
    else:
        print("\nNo jobs were loaded. Check for errors above.")

if __name__ == "__main__":
    main()
