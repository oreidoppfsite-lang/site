# O Rei do PPF — site / blog

Protótipo do site-blog da O Rei do PPF (película de proteção de pintura).

- `index.html`: página única (serviços, diário de trabalhos, história, processo, avaliações e contato pelo WhatsApp).
- `seq/f000.jpg … f119.jpg`: quadros do vídeo do topo, que avança ao descer a página e volta ao subir.
- `seq/m/`: os mesmos quadros em 1024x576, usados no celular (menos da metade do peso).

## Trocar o vídeo do topo

Converta o MP4 em 120 quadros 1600x900 com ffmpeg e substitua a pasta `seq/`:

```
ffmpeg -i video.mp4 -vf "fps=120/DURACAO,scale=1600:900:force_original_aspect_ratio=increase,crop=1600:900" -q:v 4 -start_number 0 seq/f%03d.jpg
for f in seq/f*.jpg; do ffmpeg -y -i $f -vf scale=1024:576 -q:v 5 seq/m/$(basename $f); done
```

## Aviso

Telefone, posts do diário, história e avaliações são conteúdo de exemplo. Os posts publicados pelo botão "+ Publicar trabalho" ficam só no navegador (localStorage).

Quadros provisórios renderizados a partir do modelo 3D "Ferrari 458 Italia" de vicent091036 (CC BY 4.0).
