-- Segurança: só quem está na lista de adms pode publicar, editar e apagar.
-- Antes, QUALQUER conta logada era tratada como adm. Se o cadastro público do Supabase
-- estiver ligado (vem ligado por padrão), qualquer pessoa poderia criar uma conta e apagar tudo.
--
-- Como usar:
-- 1. Crie as contas em Authentication → Users (a sua e a do dono).
-- 2. Troque os e-mails na linha marcada abaixo e rode este arquivo inteiro no SQL Editor.
-- 3. Em Authentication → Sign In / Providers → Email, desligue "Allow new users to sign up".
-- Para adicionar outro adm depois: insert into public.adms (user_id) select id from auth.users where email = 'novo@email.com';
-- Para tirar um adm: delete from public.adms where user_id = (select id from auth.users where email = 'email@antigo.com');

create table if not exists public.adms (
  user_id uuid primary key references auth.users(id) on delete cascade,
  criado_em timestamptz not null default now()
);
alter table public.adms enable row level security;
revoke all on public.adms from anon, authenticated;

-- >>> TROQUE OS E-MAILS AQUI <<<
insert into public.adms (user_id)
select id from auth.users where email in ('oreidoppf.site@gmail.com', 'EMAIL-DO-JOAO@exemplo.com')
on conflict do nothing;

create or replace function public.e_adm() returns boolean
language sql stable security definer set search_path = public
as $$ select exists (select 1 from public.adms where user_id = auth.uid()) $$;
revoke all on function public.e_adm() from public;
grant execute on function public.e_adm() to anon, authenticated;

-- posts
drop policy if exists "dono publica" on public.posts;
drop policy if exists "dono edita"   on public.posts;
drop policy if exists "dono apaga"   on public.posts;
create policy "adm publica" on public.posts for insert to authenticated with check (public.e_adm());
create policy "adm edita"   on public.posts for update to authenticated using (public.e_adm()) with check (public.e_adm());
create policy "adm apaga"   on public.posts for delete to authenticated using (public.e_adm());

-- avaliações (visitante continua podendo enviar pendente; ver tudo/aprovar/apagar só adm)
drop policy if exists "adm ve tudo" on public.avaliacoes;
drop policy if exists "adm envia"   on public.avaliacoes;
drop policy if exists "adm aprova"  on public.avaliacoes;
drop policy if exists "adm apaga"   on public.avaliacoes;
create policy "logado ve aprovadas ou adm ve tudo" on public.avaliacoes for select to authenticated using (aprovada or public.e_adm());
create policy "logado envia pendente ou adm envia" on public.avaliacoes for insert to authenticated with check (aprovada = false or public.e_adm());
create policy "adm aprova" on public.avaliacoes for update to authenticated using (public.e_adm()) with check (public.e_adm());
create policy "adm apaga"  on public.avaliacoes for delete to authenticated using (public.e_adm());

-- vídeos
drop policy if exists "adm adiciona"   on public.videos;
drop policy if exists "adm remove"     on public.videos;
drop policy if exists "adm troca capa" on public.videos;
create policy "adm adiciona"   on public.videos for insert to authenticated with check (public.e_adm());
create policy "adm remove"     on public.videos for delete to authenticated using (public.e_adm());
create policy "adm troca capa" on public.videos for update to authenticated using (public.e_adm()) with check (public.e_adm());

-- fotos (armazenamento)
drop policy if exists "fotos: dono envia"     on storage.objects;
drop policy if exists "fotos: dono apaga"     on storage.objects;
drop policy if exists "avaliacoes: adm apaga" on storage.objects;
create policy "fotos: adm envia"      on storage.objects for insert to authenticated with check (bucket_id = 'fotos' and public.e_adm());
create policy "fotos: adm apaga"      on storage.objects for delete to authenticated using (bucket_id = 'fotos' and public.e_adm());
create policy "avaliacoes: adm apaga" on storage.objects for delete to authenticated using (bucket_id = 'avaliacoes' and public.e_adm());

-- Confira: deve listar as contas de adm
select u.email from public.adms a join auth.users u on u.id = a.user_id;
