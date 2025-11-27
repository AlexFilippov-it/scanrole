#!/usr/bin/env python3
"""
LinkedIn Jobs Scraper with Supabase Integration
Сохраняет результаты скрапинга в базу данных Supabase
"""

import os
import pandas as pd
from supabase import create_client, Client
from linkedin_jobs_search_scraper import *  # Import existing scraper functions

# Supabase configuration
SUPABASE_URL = "https://ohxveapplmhyhdrkyrtq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9oeHZlYXBwbG1oeWhkcmt5cnRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxMTMyMzEsImV4cCI6MjA3OTY4OTIzMX0.Uu3V32_9-DXvF4DUJCrCx_NeKZHRwkHq5l8BcN36o4k"

def init_supabase_client() -> Client:
    """Initialize Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_jobs_to_supabase(supabase: Client, jobs_data: list, search_params: dict):
    """Save scraped jobs to Supabase database"""
    try:
        # First, create a search query record
        search_record = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000',  # Test user for now
            'search_term': search_params.get('search_term', ''),
            'country_code': search_params.get('country_code', ''),
            'location': search_params.get('location', ''),
            'job_type': search_params.get('job_type'),
            'is_remote': search_params.get('is_remote', False),
            'distance': search_params.get('distance'),
            'easy_apply': search_params.get('easy_apply', False),
            'results_count': len(jobs_data)
        }

        # Insert search query
        search_response = supabase.table('search_queries').insert(search_record).select().single()
        if search_response.status_code != 200:
            print(f"Warning: Failed to save search query: {search_response}")
            query_id = None
        else:
            query_id = search_response.data['query_id']

        # Save jobs
        saved_count = 0
        for job in jobs_data:
            # Transform job data to match our schema
            job_record = {
                'query_id': query_id,
                'linkedin_job_id': job.get('Job URL', '').split('-')[-1] if job.get('Job URL') else None,
                'title': job.get('Title', ''),
                'company': job.get('Company', ''),
                'location': job.get('Location', ''),
                'description': job.get('Description'),  # Add description if available
                'job_type': search_params.get('job_type'),
                'is_remote': search_params.get('is_remote', False),
                'easy_apply': search_params.get('easy_apply', False),
                'application_url': job.get('Job URL'),
                'company_logo_url': job.get('Logo URL')
            }

            # Remove None values
            job_record = {k: v for k, v in job_record.items() if v is not None}

            try:
                response = supabase.table('jobs').insert(job_record).select()
                if response.status_code == 200:
                    saved_count += 1
                    print(f"✓ Saved job: {job_record['title']} at {job_record['company']}")
                else:
                    print(f"✗ Failed to save job: {response}")
            except Exception as e:
                print(f"✗ Error saving job {job_record.get('title', 'Unknown')}: {e}")

        print(f"\nSaved {saved_count} out of {len(jobs_data)} jobs to Supabase")
        return saved_count

    except Exception as e:
        print(f"✗ Error saving to Supabase: {e}")
        return 0

def main():
    print("LinkedIn Jobs Scraper with Supabase Integration")
    print("=" * 50)

    # Initialize Supabase
    supabase = init_supabase_client()
    print("✓ Supabase client initialized")

    # Run the existing scraper logic
    print("\n📊 Starting job scraping...")

    # This would normally call your scraping function
    # For now, we'll simulate with sample data
    sample_jobs = [
        {
            'Title': 'Data Scientist',
            'Company': 'Tech Corp',
            'Location': 'San Francisco, CA',
            'Date Posted': '2024-01-15',
            'Logo URL': 'https://example.com/logo.png',
            'Job URL': 'https://linkedin.com/jobs/view/data-scientist-123'
        },
        {
            'Title': 'Machine Learning Engineer',
            'Company': 'AI Solutions',
            'Location': 'Remote',
            'Date Posted': '2024-01-14',
            'Logo URL': 'https://example.com/logo2.png',
            'Job URL': 'https://linkedin.com/jobs/view/ml-engineer-456'
        }
    ]

    # Current search parameters (from your scraper)
    search_params = {
        'search_term': search_term,  # from your scraper
        'country_code': country_code,
        'location': location,
        'job_type': job_type,
        'is_remote': is_remote,
        'distance': distance,
        'easy_apply': easy_apply,
        'results_wanted': results_wanted
    }

    # Save to Supabase
    saved_count = save_jobs_to_supabase(supabase, sample_jobs, search_params)

    print("
" + "=" * 50)
    print("Scraping and database integration completed!")
    print(f"📊 Jobs saved to database: {saved_count}")
    print("\nNext steps:")
    print("1. Integrate this with your actual scraping logic")
    print("2. Add user authentication")
    print("3. Create web interface for job browsing")

if __name__ == "__main__":
    main()
