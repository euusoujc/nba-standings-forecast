"""Gera o vídeo explicativo e o áudio-guia de estudo (PT e EN).

Requisitos: pip install edge-tts imageio-ffmpeg ; Google Chrome instalado.

Uso:
    py midia/build/capturar_slides.py <work>      # 1x: PNGs dos slides
    py midia/build/gerar_midia.py <work> [video|audio|all] [pt|en|all]

Saídas em midia/: video_explicativo_<lang>.mp4 (+ .srt), audio_guia_<lang>.mp3
(com capítulos) e audio_guia_<lang>/NN - <slide>.mp3.
"""
from __future__ import annotations

import asyncio, hashlib, html, json, re, subprocess, sys
from pathlib import Path

import edge_tts
import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).parent))
from cenas_video import SCENES  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MIDIA = ROOT / "midia"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = {"pt": "pt-BR-AntonioNeural", "en": "en-US-AndrewNeural"}
PAD_IN, PAD_OUT = 0.45, 0.75   # silêncio antes/depois da fala em cada cena (s)
FPS = 30

SECTIONS = {"pt": ["Tema", "Bases e fontes", "Metodologia", "Resultados e análises"],
            "en": ["Topic", "Data and sources", "Methodology", "Results and analysis"]}
BRAND = {"pt": "15 jogos não são uma temporada", "en": "15 games are not a season"}


# ------------------------------------------------------------------ utilidades
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"falhou: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-2000:]}")
    return r


def duration(path: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True, errors="replace")
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def speakable(text: str, lang: str) -> str:
    """Ajustes para a voz: '2010-2011' é lido como intervalo, não subtração."""
    return re.sub(r"\b(\d{4})-(\d{2,4})\b", r"\1, \2", text)


async def _tts(text, voice, mp3: Path, srt: Path, rate="+0%"):
    for attempt in range(5):
        try:
            com = edge_tts.Communicate(text, voice, rate=rate, boundary="SentenceBoundary")
            sub = edge_tts.SubMaker()
            with open(mp3, "wb") as f:
                async for chunk in com.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                        sub.feed(chunk)
            srt.write_text(sub.get_srt(), encoding="utf-8")
            return
        except Exception as e:  # rede instável: tenta de novo
            print(f"   TTS falhou ({type(e).__name__}: {e}); nova tentativa")
            await asyncio.sleep(2 * (attempt + 1))
    raise RuntimeError("TTS falhou 5 vezes")


def tts(text, lang, out_base: Path):
    """Sintetiza com cache por hash do texto. Retorna (mp3, srt)."""
    text = speakable(text, lang)
    key = hashlib.sha1((VOICE[lang] + text).encode()).hexdigest()[:12]
    mp3, srt = out_base.with_suffix(f".{key}.mp3"), out_base.with_suffix(f".{key}.srt")
    if not (mp3.exists() and mp3.stat().st_size > 0 and srt.exists()):
        asyncio.run(_tts(text, VOICE[lang], mp3, srt))
    return mp3, srt


# ------------------------------------------------------------------ SRT
def _t2s(t):
    h, m, rest = t.split(":"); s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def _s2t(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600_000); m, ms = divmod(ms, 60_000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt_cues(path: Path):
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    for b in blocks:
        lines = b.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            a, z = [x.strip() for x in lines[1].split("-->")]
            yield _t2s(a), _t2s(z), " ".join(lines[2:])


def write_srt(cues, path: Path):
    out = [f"{i}\n{_s2t(a)} --> {_s2t(z)}\n{t}\n" for i, (a, z, t) in enumerate(cues, 1)]
    path.write_text("\n".join(out), encoding="utf-8")


# ------------------------------------------------------------------ cenas HTML
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{background:#1C1B20;color:#F5F7FB;font-family:'Chakra Petch',sans-serif;position:relative}
body:before{content:"";position:absolute;inset:0;background:
 radial-gradient(900px 600px at 18% 22%,rgba(176,175,250,.10),transparent 70%),
 radial-gradient(800px 600px at 85% 80%,rgba(40,194,196,.10),transparent 70%)}
.wrap{position:absolute;inset:0;padding:96px 140px 120px;display:flex;flex-direction:column}
.eyebrow{font-family:'JetBrains Mono',monospace;color:#28C2C4;letter-spacing:.18em;font-size:20px;font-weight:500;margin-bottom:14px}
h1{font-size:64px;line-height:1.08;font-weight:700;letter-spacing:-.01em}
.accent{color:#28C2C4}
.foot{font-family:'JetBrains Mono',monospace;color:#B8BCC8;font-size:20px;margin-top:28px}
.bar{position:absolute;left:140px;right:140px;bottom:44px;display:flex;justify-content:space-between;
 font-family:'JetBrains Mono',monospace;font-size:17px;color:#7d8191;letter-spacing:.06em}
.bar b{color:#28C2C4;font-weight:500}
.content{flex:1;display:flex;gap:64px;margin-top:44px;min-height:0}
/* cards */
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;margin-top:56px}
.card{background:#2A2933;border:1px solid rgba(255,255,255,.10);border-radius:24px;padding:40px 34px;min-height:330px;
 box-shadow:0 10px 30px rgba(0,0,0,.25)}
.card .lab{font-family:'JetBrains Mono',monospace;color:#B0AFFA;font-size:18px;letter-spacing:.14em}
.card h3{font-size:38px;line-height:1.12;margin:22px 0 18px;font-weight:600}
.card p{font-size:25px;line-height:1.4;color:#B8BCC8}
/* seção */
.sec{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 160px}
.sec .num{font-family:'JetBrains Mono',monospace;font-size:34px;color:#28C2C4;letter-spacing:.2em}
.sec h1{font-size:150px;margin:18px 0 26px}
.sec p{font-size:40px;color:#B8BCC8}
.steps{display:flex;gap:18px;margin-top:90px}
.steps div{flex:1;border-top:5px solid #3a3946;padding-top:18px;font-size:26px;color:#7d8191}
.steps div.on{border-color:#28C2C4;color:#F5F7FB}
.steps div.done{border-color:#2f6f71;color:#9fa3b0}
/* código */
.code{flex:2.5;background:#16151A;border:1px solid rgba(255,255,255,.10);border-radius:20px;overflow:hidden;display:flex;flex-direction:column;
 box-shadow:0 20px 50px rgba(0,0,0,.35)}
.code .tab{background:#23222A;padding:16px 26px;font-family:'JetBrains Mono',monospace;font-size:19px;color:#B8BCC8;display:flex;gap:10px;align-items:center}
.code .tab i{width:13px;height:13px;border-radius:50%;display:inline-block;background:#FF7B9C}
.code .tab i:nth-child(2){background:#F6C177}.code .tab i:nth-child(3){background:#6EE7B7;margin-right:14px}
.code pre{padding:24px 28px;font-family:'JetBrains Mono',monospace;font-size:19.5px;line-height:1.55;color:#E6E8EE;white-space:pre}
.ln{color:#55586a;display:inline-block;width:46px;text-align:right;margin-right:22px;user-select:none}
.k{color:#B0AFFA}.s{color:#6EE7B7}.c{color:#7d8191;font-style:italic}.n{color:#F6C177}.f{color:#28C2C4}
.notes{flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px}
.note{border-left:4px solid #28C2C4;padding:6px 0 6px 24px;font-size:27px;line-height:1.3;color:#F5F7FB}
/* tabela */
table{border-collapse:separate;border-spacing:0;width:100%;margin-top:50px;font-size:27px;background:#2A2933;border-radius:20px;overflow:hidden}
th{font-family:'JetBrains Mono',monospace;font-size:19px;letter-spacing:.08em;color:#28C2C4;text-align:left;padding:20px 24px;background:#23222A;font-weight:500}
td{padding:17px 24px;border-top:1px solid rgba(255,255,255,.08);color:#E6E8EE}
td:last-child{font-family:'JetBrains Mono',monospace;color:#F6C177}
table.mono td{font-family:'JetBrains Mono',monospace;font-size:21px;color:#E6E8EE;padding:16px 18px}
table.mono th{padding:18px}
/* figura */
.figcard{background:#fff;border-radius:24px;padding:22px;display:flex;align-items:center;justify-content:center;box-shadow:0 20px 50px rgba(0,0,0,.35)}
.figcard img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.side .figcard{flex:1.5}
.side .notes{flex:1}
.center{justify-content:center;padding-bottom:150px}
.center .cards{margin-top:64px}.card{min-height:380px}
.wide .figcard{flex:1;min-height:0}
/* pipeline */
.pipe{display:flex;align-items:stretch;gap:0;margin-top:90px}
.node{flex:1;background:#2A2933;border:1px solid rgba(255,255,255,.10);border-radius:20px;padding:30px 18px;text-align:center}
.node .fn{font-family:'JetBrains Mono',monospace;color:#28C2C4;font-size:21px;font-weight:700}
.node .ix{font-family:'JetBrains Mono',monospace;color:#7d8191;font-size:17px;margin-bottom:12px}
.node p{font-size:25px;color:#B8BCC8;margin-top:14px;line-height:1.3}
.arrow{width:34px;display:flex;align-items:center;justify-content:center;color:#B0AFFA;font-size:30px}
"""

KW = r"\b(def|class|return|if|not|and|or|for|in|from|import|as|with|try|except|None|True|False|lambda|self)\b"
TOK = re.compile(r'(?P<c>#[^\n]*)|(?P<s>[fr]?"""[\s\S]*?"""|[fr]?"[^"\n]*"|[fr]?\'[^\'\n]*\')|(?P<k>' + KW +
                 r')|(?P<n>\b\d[\d_.]*\b)|(?P<f>(?<=def )\w+|(?<=class )\w+)')


def highlight(code: str) -> str:
    out, pos = [], 0
    for m in TOK.finditer(code):
        out.append(html.escape(code[pos:m.start()]))
        out.append(f'<span class="{m.lastgroup}">{html.escape(m.group())}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:]))
    return "".join(out)


def code_block(code, start):
    lines = highlight(code).split("\n")
    return "\n".join(f'<span class="ln">{start + i}</span>{ln}' for i, ln in enumerate(lines))


def tx(v, lang):
    return v[lang] if isinstance(v, dict) else v


def scene_html(sc, lang, sec_idx):
    t = lambda v: html.escape(tx(v, lang))
    bar = (f'<div class="bar"><span>{html.escape(BRAND[lang])}</span>'
           + (f'<span><b>{sec_idx + 1:02d}</b> · {html.escape(SECTIONS[lang][sec_idx])}</span>' if sec_idx >= 0 else "<span></span>")
           + '<span>ML · UFABC 2026.3</span></div>')
    head = lambda: f'<div class="eyebrow">{t(sc["eyebrow"])}</div><h1>{t(sc["title"])}</h1>'
    k = sc["kind"]
    if k == "section":
        i = int(sc["num"]) - 1
        steps = "".join(f'<div class="{"on" if j == i else "done" if j < i else ""}">{j + 1:02d} · {html.escape(s)}</div>'
                        for j, s in enumerate(SECTIONS[lang]))
        body = (f'<div class="sec"><div class="num">{sc["num"]} / 04</div><h1>{t(sc["title"])}</h1>'
                f'<p>{t(sc["sub"])}</p><div class="steps">{steps}</div></div>')
        bar = ""
    elif k == "cards":
        cards = "".join(f'<div class="card"><div class="lab">{t(a)}</div><h3>{t(b)}</h3><p>{t(c)}</p></div>'
                        for a, b, c in sc["cards"])
        foot = f'<div class="foot">{t(sc["foot"])}</div>' if sc.get("foot") else ""
        body = f'<div class="wrap center">{head()}<div class="cards">{cards}</div>{foot}</div>'
    elif k == "code":
        notes = "".join(f'<div class="note">{t(n)}</div>' for n in sc["notes"])
        body = (f'<div class="wrap">{head()}<div class="content"><div class="code"><div class="tab"><i></i><i></i><i></i>'
                f'{html.escape(sc["file"])}</div><pre>{code_block(sc["code"], sc["start"])}</pre></div>'
                f'<div class="notes">{notes}</div></div></div>')
    elif k == "table":
        mono = ' class="mono"' if len(sc["header"]) > 6 else ""
        th = "".join(f"<th>{t(h)}</th>" for h in sc["header"])
        trs = "".join("<tr>" + "".join(f"<td>{t(c)}</td>" for c in r) + "</tr>" for r in sc["rows"])
        foot = f'<div class="foot">{t(sc["foot"])}</div>' if sc.get("foot") else ""
        body = f'<div class="wrap center">{head()}<table{mono}><tr>{th}</tr>{trs}</table>{foot}</div>'
    elif k == "figure":
        sub = "" if lang == "pt" else "en/"
        img = (ROOT / "figures" / f"{sub}{sc['img']}").as_uri()
        if sc["layout"] == "side":
            notes = "".join(f'<div class="note">{t(n)}</div>' for n in sc.get("notes", []))
            body = (f'<div class="wrap">{head()}<div class="content side"><div class="notes">{notes}</div>'
                    f'<div class="figcard"><img src="{img}"></div></div></div>')
        else:
            body = (f'<div class="wrap" style="padding-top:70px">{head()}<div class="content wide" style="margin-top:30px">'
                    f'<div class="figcard"><img src="{img}"></div></div></div>')
    elif k == "pipeline":
        parts = []
        for i, (fn, d) in enumerate(sc["steps"]):
            if i:
                parts.append('<div class="arrow">→</div>')
            parts.append(f'<div class="node"><div class="ix">{i + 1}</div><div class="fn">{html.escape(fn)}</div><p>{t(d)}</p></div>')
        body = (f'<div class="wrap center">{head()}<div class="pipe">{"".join(parts)}</div>'
                f'<div class="foot" style="margin-top:70px">{t(sc["foot"])}</div></div>')
    else:
        raise ValueError(k)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}{bar}</body></html>'


def render_png(page: str, png: Path):
    f = png.with_suffix(".html"); f.write_text(page, encoding="utf-8")
    run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1920,1080",
         "--force-device-scale-factor=1", "--allow-file-access-from-files", "--virtual-time-budget=6000",
         f"--screenshot={png}", f.as_uri()])
    f.unlink()


# ------------------------------------------------------------------ vídeo
def build_video(work: Path, lang: str):
    d = work / f"video_{lang}"; d.mkdir(parents=True, exist_ok=True)
    segs, cues, t0, sec_idx = [], [], 0.0, -1
    for i, sc in enumerate(SCENES):
        if sc["kind"] == "section":
            sec_idx = int(sc["num"]) - 1
        png = d / f"cena_{i:02d}.png"
        if sc["kind"] == "slide":
            png = work / f"slides_{lang}" / f"slide_{sc['n']:02d}.png"
        else:
            render_png(scene_html(sc, lang, sec_idx), png)
        mp3, srt = tts(tx(sc["say"], lang), lang, d / f"fala_{i:02d}")
        dur = PAD_IN + duration(mp3) + PAD_OUT
        seg = d / f"seg_{i:02d}.mp4"
        fo = max(dur - 0.35, 0)
        run([FFMPEG, "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(png), "-i", str(mp3),
             "-filter_complex",
             f"[0:v]scale=1920:1080,format=yuv420p,fade=t=in:st=0:d=0.35,fade=t=out:st={fo:.3f}:d=0.35[v];"
             f"[1:a]aresample=48000,adelay={int(PAD_IN * 1000)}:all=1,apad[a]",
             "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}", "-r", str(FPS),
             "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage", "-crf", "20",
             "-c:a", "aac", "-b:a", "160k", "-ac", "2", str(seg)])
        real = duration(seg)
        for a, z, txt in srt_cues(srt):
            cues.append((t0 + PAD_IN + a, t0 + PAD_IN + z, txt))
        segs.append(seg); t0 += real
        print(f"  [{lang}] cena {i + 1}/{len(SCENES)} ({sc['kind']}) {real:.1f}s")
    lst = d / "lista.txt"
    lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in segs), encoding="utf-8")
    joined = d / "joined.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    srt_out = MIDIA / f"video_explicativo_{lang}.srt"
    write_srt(cues, srt_out)
    out = MIDIA / f"video_explicativo_{lang}.mp4"
    title = BRAND[lang]
    run([FFMPEG, "-y", "-i", str(joined), "-i", str(srt_out), "-map", "0", "-map", "1", "-c", "copy",
         "-c:s", "mov_text", "-metadata:s:s:0", f"language={'por' if lang == 'pt' else 'eng'}",
         "-metadata", f"title={title}", "-movflags", "+faststart", str(out)])
    print(f"OK {out.name}: {duration(out) / 60:.1f} min")


# ------------------------------------------------------------------ áudio-guia
def build_audio(work: Path, lang: str):
    d = work / f"audio_{lang}"; d.mkdir(parents=True, exist_ok=True)
    text = (MIDIA / f"narracao_guia_{lang}.txt").read_text(encoding="utf-8")
    parts = re.findall(r"^### (.+?)\n(.*?)(?=^### |\Z)", text, flags=re.S | re.M)
    tracks_dir = MIDIA / f"audio_guia_{lang}"; tracks_dir.mkdir(exist_ok=True)
    for old in tracks_dir.glob("*.mp3"):
        old.unlink()
    pieces, chapters, t0 = [], [], 0.0
    gap = d / "pausa.mp3"
    run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "1.2", "-c:a", "libmp3lame", "-b:a", "96k", str(gap)])
    for i, (title, body) in enumerate(parts):
        body = re.sub(r"\n{2,}", "\n\n", body.strip())
        mp3, _ = tts(body, lang, d / f"parte_{i:02d}")
        # normaliza para 48 kHz mono 96k (concat sem recodificar depois)
        norm = d / f"norm_{i:02d}.mp3"
        run([FFMPEG, "-y", "-i", str(mp3), "-ar", "48000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "96k", str(norm)])
        num, name = title.split(" — ", 1)
        safe = re.sub(r'[\\/:*?"<>|]', "-", name)
        track = tracks_dir / f"{num} - {safe}.mp3"
        run([FFMPEG, "-y", "-i", str(norm), "-c", "copy", "-metadata", f"title={name}",
             "-metadata", f"track={int(num) + 1}", "-metadata", f"album={BRAND[lang]}", str(track)])
        dur = duration(norm)
        chapters.append((t0, t0 + dur + 1.2, name))
        pieces += [norm, gap]; t0 += dur + 1.2
        print(f"  [{lang}] {title}: {dur / 60:.1f} min")
    lst = d / "lista.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in pieces), encoding="utf-8")
    meta = d / "chapters.txt"
    meta.write_text(";FFMETADATA1\ntitle=" + BRAND[lang] + (" — guia de estudo" if lang == "pt" else " — study guide") + "\n"
                    + "".join(f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(a * 1000)}\nEND={int(z * 1000)}\ntitle={n}\n"
                              for a, z, n in chapters), encoding="utf-8")
    out = MIDIA / f"audio_guia_{lang}.mp3"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(meta),
         "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", "-id3v2_version", "3", str(out)])
    print(f"OK {out.name}: {duration(out) / 60:.1f} min")


def main():
    work = Path(sys.argv[1]); what = sys.argv[2] if len(sys.argv) > 2 else "all"
    langs = ["pt", "en"] if len(sys.argv) <= 3 or sys.argv[3] == "all" else [sys.argv[3]]
    for lang in langs:
        if what in ("video", "all"):
            build_video(work, lang)
        if what in ("audio", "all"):
            build_audio(work, lang)


if __name__ == "__main__":
    main()
