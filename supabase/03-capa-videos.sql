-- Capa dos vídeos (print do reel, guardado na pasta fotos/capas): o adm põe e troca
alter table public.videos add column capa text check (capa is null or capa like 'https://vktidxurujnhcnhauqmj.supabase.co/storage/v1/object/public/fotos/%');
grant update on public.videos to authenticated;
create policy "adm troca capa" on public.videos for update to authenticated using (true) with check (true);
