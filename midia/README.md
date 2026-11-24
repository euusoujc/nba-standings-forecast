# Mídia: vídeo explicativo e áudio-guia de estudo

| Arquivo | O que é |
|---|---|
| `video_explicativo_pt.mp4` / `_en.mp4` | Vídeo narrado (1920×1080) do trabalho: tema, bases e fontes, metodologia, resultados e análises. Mostra os slides, o código de cada fase, as tabelas e as figuras. Legendas embutidas (faixa opcional) e em `.srt`. |
| `audio_guia_pt.mp3` / `_en.mp3` | Narração completa do guia de explicação (`apresentacao/guia_explicacao_*.txt`), slide a slide, mais o glossário. Tem capítulos por slide. |
| `audio_guia_pt/` / `audio_guia_en/` | O mesmo áudio dividido em faixas, uma por slide, para estudar por partes. |
| `narracao_guia_pt.txt` / `_en.txt` | Texto narrado no áudio-guia (o guia reescrito para ser falado). |
| `build/cenas_video.py` | Roteiro do vídeo: cada cena com o visual e a fala, em PT e EN. |

As vozes são neurais (Microsoft Edge TTS, via `edge-tts`): `pt-BR-AntonioNeural` e `en-US-AndrewNeural`.

## Como regenerar

Requer Google Chrome e `pip install edge-tts imageio-ffmpeg` (o TTS precisa de internet).

```powershell
py midia/build/capturar_slides.py $env:TEMP\nba_midia
py midia/build/gerar_midia.py $env:TEMP\nba_midia all all
```

O segundo argumento escolhe `video`, `audio` ou `all`; o terceiro, `pt`, `en` ou `all`. Rode `capturar_slides.py` de novo
sempre que mudar os slides. As falas ficam em cache pelo texto, então só as cenas alteradas são sintetizadas de novo.
