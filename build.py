"""Build resume PDFs from resume.tex (Tectonic/LaTeX).

Usage:
  python build.py                 # build all variants
  python build.py full            # build one variant: full | software | ml
  python build.py full --deploy   # build, commit, push (Pages serves resume.pdf)

Variants write resume_<variant>.pdf; `full` additionally writes resume.pdf
(the public default deployed to GitHub Pages).
"""
import shutil, subprocess, sys, os, tempfile

REPO = os.path.dirname(os.path.abspath(__file__))
TECTONIC = r"C:\Users\yashs\Tools\tectonic\tectonic.exe"
SRC = os.path.join(REPO, "resume.tex")

# variant -> toggles written to variant.tex
VARIANTS = {
    "full":     ["\\inclhardwaretrue",  "\\inclrecentfalse", "\\mlleadfalse"],
    "software": ["\\inclhardwarefalse", "\\inclrecentfalse", "\\mlleadfalse"],
    "ml":       ["\\inclhardwaretrue",  "\\inclrecenttrue",  "\\mlleadtrue"],
}

def build(variant: str) -> str:
    outdir = os.path.join(REPO, "build")
    os.makedirs(outdir, exist_ok=True)
    if variant == "cv":
        tex = os.path.join(outdir, "cv.tex")
        shutil.copy(os.path.join(REPO, "cv.tex"), tex)
        imgdst = os.path.join(outdir, "img")
        os.makedirs(imgdst, exist_ok=True)
        for jf in os.listdir(os.path.join(REPO, "img")):
            shutil.copy(os.path.join(REPO, "img", jf), os.path.join(imgdst, jf))
    else:
        tex = os.path.join(outdir, f"resume_{variant}.tex")
        shutil.copy(SRC, tex)
        vf = os.path.join(outdir, "variant.tex")
        with open(vf, "w", encoding="utf-8") as f:
            f.write("% variant toggles (auto-generated)\n")
            for line in VARIANTS[variant]:
                f.write(line + "\n")
    r = subprocess.run([TECTONIC, tex],
                       cwd=outdir, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(r.stdout[-3000:]); print(r.stderr[-3000:])
        raise SystemExit(f"tectonic failed for {variant}")
    pdf = os.path.join(outdir, f"resume_{variant}.pdf" if variant != "cv" else "cv.pdf")
    dst = os.path.join(REPO, os.path.basename(pdf))
    shutil.copy(pdf, dst)
    print(f"built: {os.path.basename(dst)} ({os.path.getsize(dst)} bytes)")
    if variant == "full":
        shutil.copy(pdf, os.path.join(REPO, "resume.pdf"))
        print("built: resume.pdf (public default)")
    return dst

def deploy():
    def sh(*args):
        r = subprocess.run(list(args), cwd=REPO, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout, r.stderr); raise SystemExit("git step failed")
    sh("git", "add", "resume.tex", "cv.tex", "build.py", "index.html",
       "resume.pdf", "resume_full.pdf", "resume_software.pdf", "resume_ml.pdf", "cv.pdf")
    sh("git", "add", "img/diagram_swarm.jpg", "img/diagram_sesame.jpg", "img/diagram_campass.jpg", "img/diagram_ops.jpg")
    sh("git", "add", ".gitignore")
    sh("git", "commit", "-m", "resume + cv: LaTeX sources (tectonic) and built PDFs")
    sh("git", "push", "origin", "HEAD")
    print("deployed -> https://yashop965.github.io/resume/resume.pdf and .../cv.pdf")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    do_deploy = "--deploy" in args
    targets = list(VARIANTS) + ["cv"]
    names = [a for a in args if a in targets] or targets
    for n in names:
        build(n)
    if do_deploy:
        deploy()
