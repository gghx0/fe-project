# No-login Solution Submissions

The `/submit` page reads and writes pending submissions through Supabase using public anon access. Visitors do not need to log in.

Visitors can delete their own pending submissions from the same browser they used to submit. The browser keeps a private delete token; Supabase stores only its SHA-256 hash.

## Required public environment values

Set these in `website/.env` for local development and as GitHub repository variables or repository secrets for Pages builds:

```sh
PUBLIC_SUPABASE_URL=https://your-project.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-public-anon-key
```

The anon key is intentionally public. Do not use a service-role key in this site.

## Supabase table and policies

Run this SQL in the Supabase SQL editor:

```sql
create extension if not exists pgcrypto;

create table if not exists public.solution_submissions (
  id uuid primary key default gen_random_uuid(),
  fe_id text not null check (fe_id ~ '^FE-[0-9]{4}$'),
  problem_number integer not null check (
    problem_number between 1 and 847
  ),
  username text not null check (
    char_length(trim(username)) between 1 and 80
  ),
  solution text not null check (
    char_length(trim(solution)) between 20 and 20000
  ),
  delete_token_hash text not null check (
    delete_token_hash ~ '^[a-f0-9]{64}$'
  ),
  status text not null default 'pending' check (
    status in ('pending', 'accepted', 'rejected')
  ),
  submitted_at timestamptz not null default now()
);

alter table public.solution_submissions
  add column if not exists delete_token_hash text;

update public.solution_submissions
set delete_token_hash = encode(
  digest(gen_random_uuid()::text, 'sha256'),
  'hex'
)
where delete_token_hash is null;

alter table public.solution_submissions
  alter column delete_token_hash set not null;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'solution_submissions_delete_token_hash_check'
      and conrelid = 'public.solution_submissions'::regclass
  ) then
    alter table public.solution_submissions
      add constraint solution_submissions_delete_token_hash_check
      check (delete_token_hash ~ '^[a-f0-9]{64}$');
  end if;
end $$;

create index if not exists
  solution_submissions_pending_order_idx
on public.solution_submissions (
  status,
  submitted_at desc
);

alter table public.solution_submissions
  enable row level security;

revoke all on public.solution_submissions from anon;

grant select (
  id,
  fe_id,
  problem_number,
  username,
  solution,
  status,
  submitted_at
) on public.solution_submissions to anon;

grant insert (
  fe_id,
  problem_number,
  username,
  solution,
  status,
  delete_token_hash
) on public.solution_submissions to anon;

drop policy if exists
  "Visitors can read pending submissions"
on public.solution_submissions;

create policy
  "Visitors can read pending submissions"
on public.solution_submissions
for select
to anon
using (status = 'pending');

drop policy if exists
  "Visitors can submit pending solutions"
on public.solution_submissions;

create policy
  "Visitors can submit pending solutions"
on public.solution_submissions
for insert
to anon
with check (
  status = 'pending'
  and delete_token_hash ~ '^[a-f0-9]{64}$'
);

create or replace function public.delete_solution_submission(
  _submission_id uuid,
  _delete_token text
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  deleted_count integer;
begin
  delete from public.solution_submissions
  where id = _submission_id
    and status = 'pending'
    and delete_token_hash = encode(
      digest(_delete_token, 'sha256'),
      'hex'
    );

  get diagnostics deleted_count = row_count;

  return deleted_count = 1;
end;
$$;

revoke all on function public.delete_solution_submission(
  uuid,
  text
) from public;

grant execute on function public.delete_solution_submission(
  uuid,
  text
) to anon;
```

To verify a submission, change its `status` to `accepted` or `rejected` in Supabase, then add the official checked solution to `solutions/FE-0000.md`. Once a submission is no longer pending, the visitor cannot delete it from the public page.
