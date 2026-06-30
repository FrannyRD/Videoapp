-- Ejecuta esto una sola vez en Supabase > SQL Editor.
-- Esta tabla guarda los videos marcados como listos/vistos.

create table if not exists public.video_status (
  video_id text primary key,
  page_id text not null,
  ready boolean not null default false,
  ready_at timestamptz,
  updated_at timestamptz not null default now()
);

create index if not exists video_status_page_id_idx
  on public.video_status(page_id);
