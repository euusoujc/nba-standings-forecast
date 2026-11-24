"""Captura cada slide de apresentacao_<lang>.html como PNG 1920x1080 (Chrome headless)."""
import subprocess, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = Path(sys.argv[1])  # pasta de trabalho

INJECT = """
<style>.animate{opacity:1!important;transform:none!important;transition:none!important;animation:none!important}
.dot-nav{display:none!important} html,body{scroll-snap-type:none!important;overflow:hidden!important}</style>
<script>
document.addEventListener('DOMContentLoaded',()=>{
  const s=[...document.querySelectorAll('section.slide')];
  s.forEach((el,i)=>{ if(i!==__K__) el.style.display='none'; });
  document.querySelectorAll('.animate').forEach(e=>e.classList.add('in'));
});
</script>
"""

def main():
    for lang in ("pt", "en"):
        html = (ROOT / "apresentacao" / f"apresentacao_{lang}.html").read_text(encoding="utf-8")
        n = len(re.findall(r'<section class="slide', html))
        d = OUT / f"slides_{lang}"; d.mkdir(parents=True, exist_ok=True)
        for k in range(n):
            page = html.replace("</body>", INJECT.replace("__K__", str(k)) + "</body>")
            f = d / f"slide_{k+1:02d}.html"; f.write_text(page, encoding="utf-8")
            png = d / f"slide_{k+1:02d}.png"
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--window-size=1920,1080", "--force-device-scale-factor=1",
                            "--virtual-time-budget=6000", f"--screenshot={png}", f.as_uri()],
                           check=True, capture_output=True)
            f.unlink()
            print(lang, k + 1, png.exists())

main()
