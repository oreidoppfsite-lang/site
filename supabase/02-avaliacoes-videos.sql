-- Avaliações: visitante envia (fica pendente); só as aprovadas aparecem; adm aprova e apaga
create table public.avaliacoes (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  nome text not null check (char_length(nome) between 2 and 60),
  carro text not null default '' check (char_length(carro) <= 60),
  nota int not null check (nota between 1 and 5),
  texto text not null check (char_length(texto) between 10 and 600),
  aprovada boolean not null default false,
  foto text check (foto is null or foto like 'https://vktidxurujnhcnhauqmj.supabase.co/storage/v1/object/public/avaliacoes/%')
);
grant select, insert on public.avaliacoes to anon;
grant select, insert, update, delete on public.avaliacoes to authenticated;
alter table public.avaliacoes enable row level security;
create policy "visitante ve aprovadas"   on public.avaliacoes for select to anon using (aprovada);
create policy "visitante envia pendente" on public.avaliacoes for insert to anon with check (aprovada = false);
create policy "adm ve tudo"  on public.avaliacoes for select to authenticated using (true);
create policy "adm envia"    on public.avaliacoes for insert to authenticated with check (true);
create policy "adm aprova"   on public.avaliacoes for update to authenticated using (true) with check (true);
create policy "adm apaga"    on public.avaliacoes for delete to authenticated using (true);

-- Fotos das avaliações (até 3 MB, só imagens): visitante envia, todos veem, adm apaga
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('avaliacoes', 'avaliacoes', true, 3145728, array['image/jpeg','image/png','image/webp']);
create policy "avaliacoes: todos veem"       on storage.objects for select to anon, authenticated using (bucket_id = 'avaliacoes');
create policy "avaliacoes: visitante envia"  on storage.objects for insert to anon, authenticated with check (bucket_id = 'avaliacoes');
create policy "avaliacoes: adm apaga"        on storage.objects for delete to authenticated using (bucket_id = 'avaliacoes');

-- Vídeos do Instagram: o adm cola o link; todos veem
create table public.videos (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  url text not null check (url ~ '^https://www\.instagram\.com/(reel|p|tv)/[A-Za-z0-9_-]+/$')
);
grant select on public.videos to anon, authenticated;
grant insert, delete on public.videos to authenticated;
alter table public.videos enable row level security;
create policy "todos veem"     on public.videos for select to anon, authenticated using (true);
create policy "adm adiciona"   on public.videos for insert to authenticated with check (true);
create policy "adm remove"     on public.videos for delete to authenticated using (true);
