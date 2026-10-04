# O Rei do PPF — site / blog

Protótipo do site-blog da O Rei do PPF (película de proteção de pintura).

- `index.html`: página única (serviços, diário de trabalhos, história, processo, avaliações e contato pelo WhatsApp).
- `video/`: vídeo do topo, que toca sozinho, sem som, em loop. `topo-v.mp4` é o recorte vertical para celular em pé, `topo-hd.mp4` (1080p) vai para telas largas com muitos pixels e `topo.mp4` (720p) para o resto. `topo.jpg` e `topo-v.jpg` são as imagens mostradas antes de carregar e para quem desativa animações.
- `img/`: fotos dos cartões de serviço e da história.

## Trocar o vídeo do topo

Com ffmpeg, a partir do vídeo original em 1920x1080 (sem som; o recorte vertical é para celular em pé):

```
ffmpeg -i video.mp4 -an -vf "scale=1280:720,format=yuv420p" -c:v libx264 -preset slow -crf 27 -movflags +faststart video/topo.mp4
ffmpeg -i video.mp4 -an -vf "format=yuv420p" -c:v libx264 -preset slow -crf 28 -movflags +faststart video/topo-hd.mp4
ffmpeg -i video.mp4 -an -vf "crop=608:1080:(iw-608)/2:0,format=yuv420p" -c:v libx264 -preset slow -crf 24 -movflags +faststart video/topo-v.mp4
ffmpeg -ss 5 -i video.mp4 -frames:v 1 -vf scale=1280:720 -q:v 4 video/topo.jpg
ffmpeg -ss 5 -i video.mp4 -frames:v 1 -vf "crop=608:1080:(iw-608)/2:0" -q:v 4 video/topo-v.jpg
```

`tools/render_topo.py` é o render 3D usado antes do vídeo, guardado caso volte a ser útil.

## Aviso

Telefone, posts do diário, história e avaliações são conteúdo de exemplo. Os posts publicados pelo botão "+ Publicar trabalho" ficam só no navegador (localStorage).

Quadros provisórios renderizados a partir do modelo 3D "Ferrari 458 Italia" de vicent091036 (CC BY 4.0).
