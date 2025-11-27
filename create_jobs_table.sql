-- Таблица для хранения вакансий из LinkedIn скрапера
CREATE TABLE IF NOT EXISTS public.scraped_jobs (
  job_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  linkedin_job_id TEXT UNIQUE, -- ID вакансии из LinkedIn URL
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  date_posted_text TEXT, -- Оригинальный текст из LinkedIn
  logo_url TEXT,
  job_url TEXT UNIQUE NOT NULL,
  search_query TEXT, -- По какому запросу найдена вакансия
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_scraped_jobs_linkedin_id ON public.scraped_jobs(linkedin_job_id);
CREATE INDEX IF NOT EXISTS idx_scraped_jobs_company ON public.scraped_jobs(company);
CREATE INDEX IF NOT EXISTS idx_scraped_jobs_location ON public.scraped_jobs(location);
CREATE INDEX IF NOT EXISTS idx_scraped_jobs_search_query ON public.scraped_jobs(search_query);
CREATE INDEX IF NOT EXISTS idx_scraped_jobs_created_at ON public.scraped_jobs(created_at);

-- Row Level Security
ALTER TABLE public.scraped_jobs ENABLE ROW LEVEL SECURITY;

-- Политика: все аутентифицированные пользователи могут читать вакансии
CREATE POLICY "Authenticated users can view scraped jobs" ON public.scraped_jobs
  FOR SELECT USING (auth.role() = 'authenticated');

-- Политика: только владелец может вставлять вакансии (пока что)
CREATE POLICY "Authenticated users can insert scraped jobs" ON public.scraped_jobs
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

