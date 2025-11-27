-- LinkedIn Jobs Scraper Database Schema
-- Run this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  name TEXT,
  subscription_plan TEXT CHECK (subscription_plan IN ('free', 'premium')) DEFAULT 'free',
  search_limit INTEGER DEFAULT 100,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Search queries table (to track user searches)
CREATE TABLE IF NOT EXISTS public.search_queries (
  query_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users ON DELETE CASCADE,
  search_term TEXT NOT NULL,
  country_code TEXT NOT NULL,
  location TEXT,
  job_type TEXT,
  is_remote BOOLEAN DEFAULT FALSE,
  distance INTEGER,
  easy_apply BOOLEAN DEFAULT FALSE,
  results_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Jobs table (main table for scraped job data)
CREATE TABLE IF NOT EXISTS public.jobs (
  job_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  query_id UUID REFERENCES public.search_queries ON DELETE CASCADE,
  linkedin_job_id TEXT UNIQUE NOT NULL, -- ID from LinkedIn
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  description TEXT,
  salary_min DECIMAL,
  salary_max DECIMAL,
  salary_currency TEXT,
  job_type TEXT,
  is_remote BOOLEAN DEFAULT FALSE,
  easy_apply BOOLEAN DEFAULT FALSE,
  date_posted DATE,
  application_url TEXT,
  company_logo_url TEXT,
  skills TEXT[], -- Array of required skills
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- User favorites table
CREATE TABLE IF NOT EXISTS public.user_favorites (
  favorite_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users ON DELETE CASCADE,
  job_id UUID REFERENCES public.jobs ON DELETE CASCADE,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  UNIQUE(user_id, job_id)
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.search_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_favorites ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = user_id);

-- Search queries policies
CREATE POLICY "Users can view own search queries" ON public.search_queries
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own search queries" ON public.search_queries
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Jobs policies (jobs are visible to all authenticated users for now)
CREATE POLICY "Authenticated users can view jobs" ON public.jobs
  FOR SELECT USING (auth.role() = 'authenticated');

-- Favorites policies
CREATE POLICY "Users can view own favorites" ON public.user_favorites
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own favorites" ON public.user_favorites
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own favorites" ON public.user_favorites
  FOR DELETE USING (auth.uid() = user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_linkedin_id ON public.jobs(linkedin_job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_query_id ON public.jobs(query_id);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON public.jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON public.jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON public.jobs(date_posted);
CREATE INDEX IF NOT EXISTS idx_search_queries_user_id ON public.search_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON public.user_favorites(user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = TIMEZONE('utc'::text, NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at
  BEFORE UPDATE ON public.jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

