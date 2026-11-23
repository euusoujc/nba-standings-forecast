"""Monta as apresentações HTML (arquivo único) a partir do template da skill.

- slides_<lang>.body.html: conteúdo dos slides
- template.html: motor (CSS + navegação) da skill construtor-apresentacoes
- imagens (IMG:nome.png) são embutidas em base64 a partir de figures/ (pt) ou figures/en/ (en)

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
"""


def inline_images(html: str, figdir: Path) -> str:
    def repl(m):
        data = base64.b64encode((figdir / m.group(1)).read_bytes()).decode()
        return f"data:image/png;base64,{data}"
    return re.sub(r"IMG:([\w\-]+\.png)", repl, html)


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
    html = inline_images(html, figdir)
    out = HERE / f"apresentacao_{lang}.html"
    out.write_text(html, encoding="utf-8")
    n = html.count('class="slide ')
    print(f"{out.name}: {n} slides, {len(html) / 1e6:.1f} MB")


if __name__ == "__main__":
    build("en", "15 Games Are Not a Season")
    build("pt", "15 Jogos Não São uma Temporada")
