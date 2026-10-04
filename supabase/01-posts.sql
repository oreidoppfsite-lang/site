-- Diário: tabela dos posts e pasta das fotos (já aplicado no projeto rei-do-ppf)
create table public.posts (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  data date not null default current_date,
  carro text not null check (char_length(carro) between 1 and 80),
  servico text not null check (servico in ('full','parcial','pontual')),
  titulo text not null check (char_length(titulo) between 1 and 140),
  texto text not null default '' check (char_length(texto) <= 4000),
  fotos text[] not null default '{}'
);
grant select on public.posts to anon, authenticated;
grant insert, update, delete on public.posts to authenticated;
alter table public.posts enable row level security;
create policy "todos leem"   on public.posts for select to anon, authenticated using (true);
create policy "dono publica" on public.posts for insert to authenticated with check (true);
create policy "dono edita"   on public.posts for update to authenticated using (true) with check (true);
create policy "dono apaga"   on public.posts for delete to authenticated using (true);

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('fotos', 'fotos', true, 5242880, array['image/jpeg','image/png','image/webp']);
create policy "fotos: todos veem" on storage.objects for select to anon, authenticated using (bucket_id = 'fotos');
create policy "fotos: dono envia" on storage.objects for insert to authenticated with check (bucket_id = 'fotos');
create policy "fotos: dono apaga" on storage.objects for delete to authenticated using (bucket_id = 'fotos');
