"""Monta as apresentações HTML (arquivo único) a partir do template da skill.

- slides_<lang>.body.html: conteúdo dos slides
- template.html: motor (CSS + navegação) da skill construtor-apresentacoes
- imagens (IMG:nome.png) são embutidas em base64 a partir de figures/ (pt) ou figures/en/ (en)
- logo e fotos (ASSET:nome.ext) vêm de apresentacao/img/; fotos de atletas que não existirem são puladas

Uso: python apresentacao/build.py
"""
import base64
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = HERE / "template.html"

EXTRA_CSS = """
    /* ---- extensões do deck NBA ---- */
    .hl { color: var(--text); font-weight: 600; }
    .dim { color: var(--text-soft); }
    .footnote { font-size: var(--fs-mono); color: var(--text-soft); margin-top: 6px; }
    .muted-card { opacity: 0.78; }
    .card--accent { border-color: rgba(40,194,196,0.30) !important; box-shadow: var(--shadow-glow) !important; }
    .node-accent { border-color: rgba(40,194,196,0.30); box-shadow: var(--shadow-glow); }
    .feature-grid .feature-card h3 { font-size: clamp(20px, 1.9vw, 26px); }
    .feature-card p, .diagram-node p { font-size: 16px; }
    .stat-card p { font-size: 16px; }
    .stats-grid .stat-value { font-size: clamp(56px, 7vw, 112px); }
    .split { display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr); gap: 48px; align-items: center; }
    .split .section-heading p { font-size: var(--fs-body-lg); line-height: 1.45; }
    .screenshot-frame { background: #ffffff; padding: 10px; margin: 0; }
    .screenshot-frame img { max-height: 70vh; width: auto; max-width: 100%; margin: 0 auto; object-fit: contain; }
    .wide-frame img { max-height: 62vh; }
    h2.wide { max-width: 32ch; font-size: clamp(24px, 2.6vw, 36px); }
    .statement { max-width: 16ch; }
    @media (max-width: 1100px) { .split { grid-template-columns: 1fr; gap: 24px; } }

    /* ---- identidade NBA: logo, fotos de atletas e créditos ---- */
    .slide-bg { position: absolute; inset: 0; z-index: 0; background-size: cover; background-position: center right; }
    .slide-bg::after { content: ""; position: absolute; inset: 0;
      background: linear-gradient(90deg, var(--bg) 0%, rgba(28,27,32,0.94) 34%, rgba(28,27,32,0.62) 62%, rgba(28,27,32,0.30) 100%),
                  linear-gradient(0deg, rgba(28,27,32,0.85) 0%, transparent 35%); }
    .nba-logo { height: 64px; width: auto; align-self: flex-start; background: #fff; border-radius: 14px;
      padding: 8px 12px; box-shadow: var(--shadow-soft); }
    .nba-logo.small { height: 44px; padding: 6px 9px; border-radius: 10px; }
    .credit { position: absolute; left: var(--container-pad-x); right: 120px; bottom: 18px; z-index: 2;
      font-family: "JetBrains Mono", monospace; font-size: 11px; letter-spacing: 0.02em; color: var(--text-soft); opacity: 0.8; }
    .proj-head { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 32px; align-items: end; }
    .players { display: flex; gap: 16px; }
    .player-card { margin: 0; width: 132px; border-radius: var(--radius-sm); overflow: hidden; background: var(--surface);
      border: 1px solid var(--line); box-shadow: var(--shadow-soft); }
    .player-card img { display: block; width: 100%; height: 150px; object-fit: cover; object-position: center 20%; }
    .player-card figcaption { padding: 7px 9px 8px; font-family: "JetBrains Mono", monospace; font-size: 11px;
      line-height: 1.35; color: var(--text-soft); }
    .player-card figcaption b { display: block; color: var(--text); font-size: 12px; }
    .player-card figcaption .accent-text { font-weight: 700; }
    .proj-slide .wide-frame img { max-height: 54vh; }
    .q-split { display: flex; align-items: center; justify-content: space-between; gap: 48px; }
    .q-split > div { flex: 1; min-width: 0; }
    .statement span { white-space: nowrap; }
    .player-card.tall { width: clamp(220px, 22vw, 300px); flex-shrink: 0; }
    .player-card.tall img { height: clamp(280px, 46vh, 400px); object-position: center 15%; }
    .player-card.tall figcaption { font-size: 12px; }
    @media (max-width: 1100px) { .proj-head { grid-template-columns: 1fr; } }
"""

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def inline_images(html: str, figdir: Path) -> str:
    def repl(m):
        data = base64.b64encode((figdir / m.group(1)).read_bytes()).decode()
        return f"data:image/png;base64,{data}"
    return re.sub(r"IMG:([\w\-]+\.png)", repl, html)


def inline_assets(html: str) -> str:
    """ASSET:nome.ext -> imagem de apresentacao/img/ embutida em base64.

    Um <figure class="player-card"> cujo arquivo não existe é removido (foto opcional)."""
    imgdir = HERE / "img"

    def drop_missing(m):
        name = re.search(r"ASSET:([\w\-.]+)", m.group(0)).group(1)
        if (imgdir / name).exists():
            return m.group(0)
        print(f"  aviso: {name} não está em apresentacao/img/; card removido")
        return ""
    html = re.sub(r'[ \t]*<figure class="player-card[^"]*">.*?</figure>\n?', drop_missing, html, flags=re.S)

    def repl(m):
        f = imgdir / m.group(1)
        data = base64.b64encode(f.read_bytes()).decode()
        return f"data:{MIME[f.suffix.lower()]};base64,{data}"
    return re.sub(r"ASSET:([\w\-]+\.(?:png|jpe?g|webp))", repl, html)


def build(lang: str, title: str):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    body = (HERE / f"slides_{lang}.body.html").read_text(encoding="utf-8")
    head, rest = tpl.split('<main class="presentation">', 1)
    _, tail = rest.split("</main>", 1)
    head = head.replace('<html lang="en">', f'<html lang="{"pt-BR" if lang == "pt" else "en"}">')
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head)
    head = head.replace("  </style>", EXTRA_CSS + "  </style>", 1)
    if lang == "pt":
        tail = tail.replace("Go to slide", "Ir para o slide")
    html = head + '<main class="presentation">\n' + body + "\n  </main>" + tail
    figdir = ROOT / "figures" / ("en" if lang == "en" else "")
    html = inline_assets(inline_images(html, figdir))
    out = HERE / f"apresentacao_{lang}.html"
    out.write_text(html, encoding="utf-8")
    n = html.count('class="slide ')
    print(f"{out.name}: {n} slides, {len(html) / 1e6:.1f} MB")


if __name__ == "__main__":
    build("en", "15 Games Are Not a Season")
    build("pt", "15 Jogos Não São uma Temporada")
