-- Run this in Supabase SQL Editor to create all required tables

-- Users table (extends Supabase auth.users)
create table if not exists public.users (
  id uuid references auth.users(id) on delete cascade primary key,
  email text not null,
  preferred_language text not null default 'en',
  role text not null default 'patient',
  created_at timestamptz default now()
);

-- Documents table
create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete cascade not null,
  file_path text not null,
  source_language text,
  status text not null default 'upload',
  uploaded_at timestamptz default now()
);

-- Document texts table (OCR + translations)
create table if not exists public.document_texts (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references public.documents(id) on delete cascade not null unique,
  ocr_text text,
  english_translation text,
  user_language_translation text,
  updated_at timestamptz default now()
);

-- Health passports table
create table if not exists public.health_passports (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references public.documents(id) on delete cascade not null unique,
  structured_json jsonb not null,
  patient_confirmed boolean not null default false,
  generated_at timestamptz default now()
);

-- Risk checks table
create table if not exists public.risk_checks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references public.documents(id) on delete cascade not null unique,
  risk_score text not null,
  issues jsonb not null default '[]',
  requires_review boolean not null default false,
  checked_at timestamptz default now()
);

-- Add error_message to documents
alter table public.documents add column if not exists error_message text;

-- Enable Row Level Security
alter table public.users enable row level security;
alter table public.documents enable row level security;
alter table public.document_texts enable row level security;
alter table public.health_passports enable row level security;

-- RLS Policies: users can only access their own data
create policy "users_own" on public.users
  for all using (auth.uid() = id);

create policy "documents_own" on public.documents
  for all using (auth.uid() = user_id);

create policy "document_texts_own" on public.document_texts
  for all using (
    document_id in (select id from public.documents where user_id = auth.uid())
  );

create policy "passports_own" on public.health_passports
  for all using (
    document_id in (select id from public.documents where user_id = auth.uid())
  );

alter table public.risk_checks enable row level security;

create policy "risk_checks_own" on public.risk_checks
  for all using (
    document_id in (select id from public.documents where user_id = auth.uid())
  );

-- Storage bucket for uploaded files
insert into storage.buckets (id, name, public)
values ('documents', 'documents', false)
on conflict do nothing;

do $$
begin
  if not exists (
    select 1 from pg_policies where policyname = 'storage_own' and tablename = 'objects'
  ) then
    execute $policy$
      create policy "storage_own" on storage.objects
        for all using (auth.uid()::text = (storage.foldername(name))[1])
    $policy$;
  end if;
end $$;

-- Help requests table (for "Need more help?" feature)
create table if not exists public.help_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete cascade not null,
  message text not null,
  status text not null default 'pending',
  created_at timestamptz default now()
);

alter table public.help_requests enable row level security;

create policy "help_requests_own" on public.help_requests
  for all using (auth.uid() = user_id);
