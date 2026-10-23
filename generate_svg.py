#!/usr/bin/env python3
"""Renders the animated SVGs used by the profile README.

  assets/hero.svg       neofetch-style terminal session
  assets/pipeline.svg   looping deploy pipeline
  assets/rack.svg       tech stack as a server rack
  assets/telemetry.svg  Grafana-style panel fed by the GitHub API
each with a narrower *-mobile.svg twin that README.md swaps in on phones.

Run with a token so the numbers are live:
  GITHUB_TOKEN=$(gh auth token) python3 generate_svg.py
.github/workflows/profile.yml reruns this daily. Without a token (or if the
API call fails) it reuses the last snapshot in assets/stats.json.

Everything is plain SVG + CSS keyframes: GitHub serves README images through
its camo proxy, so no JS, external fonts or external images are possible.
Logos in icons/ come from simple-icons (CC0).
"""
import datetime as dt
import html
import itertools
import json
import os
import random
import re
import urllib.request
from pathlib import Path

# ─────────────────── CONFIG ────────────────────────────────────────────────
ROOT   = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ICONS  = ROOT / "icons"
USER   = "SakamotoMrX"
BIRTH  = dt.date(2011, 2, 20)   # drives the "Uptime" line; adjust if off
W      = 985                    # desktop width
W_MOBILE = 420                  # served below 600px via <picture>

FONT = "'JetBrains Mono','Fira Code','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
CW   = 0.6                      # monospace advance width, in em

C = dict(
    bg="#0d1117", panel="#161b22", face="#1c2128", line="#30363d",
    text="#c9d1d9", bright="#e6edf3", muted="#8b949e", dim="#484f58",
    green="#3fb950", yellow="#d29922", red="#f85149", blue="#58a6ff",
    orange="#ffa657", cyan="#a5d6ff", purple="#d2a8ff",
)

# simple-icons brand colours; black brands are lifted so they show on dark
BRAND = dict(
    linux="FCC624", archlinux="1793D1", apple="E6EDF3", gnubash="4EAA25",
    yaml="CB171E", docker="2496ED", kubernetes="326CE5", nginx="009639",
    cloudflare="F38020", prometheus="E6522C", grafana="F46800", git="F03C2E",
    githubactions="2088FF", vercel="E6EDF3", nextdotjs="E6EDF3",
    react="61DAFB", typescript="3178C6", tailwindcss="06B6D4", php="777BB4",
    swift="F05138", tauri="24C8D8", arduino="00878F",
)

BASE_CSS = (
    "text{white-space:pre}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


# ─────────────────── HELPERS ───────────────────────────────────────────────
def esc(s):
    return html.escape(str(s), quote=True)


def T(x, y, s, fs, fill=None, cls=None, anchor="start", weight=None,
      style=None, fit=True):
    """<text>, stretched to an exact monospace width so layout never drifts
    whichever fallback font the viewer ends up with."""
    a = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-size="{fs}"']
    if fill:   a.append(f'fill="{fill}"')
    if cls:    a.append(f'class="{cls}"')
    if weight: a.append(f'font-weight="{weight}"')
    if style:  a.append(f'style="{style}"')
    if anchor != "start":
        a.append(f'text-anchor="{anchor}"')
    if fit and s.strip():
        a.append(f'textLength="{len(s) * fs * CW:.1f}" lengthAdjust="spacingAndGlyphs"')
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def icon(slug, x, y, size, color=None):
    d = re.search(r'<path d="([^"]+)"', (ICONS / f"{slug}.svg").read_text()).group(1)
    return (f'<path transform="translate({x:.1f} {y:.1f}) scale({size / 24:.4f})" '
            f'fill="{color or "#" + BRAND[slug]}" d="{d}"/>')


def pct(t, total):
    return f"{t / total * 100:.2f}%"


def svg(w, h, title, css, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}" role="img" aria-label="{esc(title)}">\n'
        f'<title>{esc(title)}</title>\n'
        f'<style>{BASE_CSS}{css}</style>\n'
        f'<defs>{defs}</defs>\n{body}\n</svg>\n'
    )


def window(w, h, title):
    """macOS-style terminal chrome; returns (defs, opening markup)."""
    defs = f'<clipPath id="win"><rect width="{w}" height="{h}" rx="10"/></clipPath>'
    body = (
        f'<g clip-path="url(#win)"><rect width="{w}" height="{h}" fill="{C["bg"]}"/>'
        f'<rect width="{w}" height="34" fill="{C["panel"]}"/>'
        f'<path d="M0 34.5H{w}" stroke="{C["line"]}"/>'
        + "".join(f'<circle cx="{20 + i * 20}" cy="17" r="6" fill="{c}"/>'
                  for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")))
        + T(w / 2, 21.5, title, 12, C["muted"], anchor="middle")
    )
    return defs, body


def border(w, h):
    return f'</g><rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" stroke="{C["line"]}"/>'


# ─────────────────── DATA ──────────────────────────────────────────────────
QUERY = """query($login:String!){user(login:$login){
  createdAt followers{totalCount}
  repositories(ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false,first:100){
    totalCount nodes{stargazerCount languages(first:10){edges{size node{name color}}}}}
  contributionsCollection{totalCommitContributions
    contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch_stats():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("no GITHUB_TOKEN")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    u = payload["data"]["user"]

    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            langs.setdefault(name, [0, e["node"]["color"] or C["muted"]])[0] += e["size"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]

    return dict(
        created=u["createdAt"][:10],
        followers=u["followers"]["totalCount"],
        repos=u["repositories"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        commits=u["contributionsCollection"]["totalCommitContributions"],
        contributions=cal["totalContributions"],
        days=days,
        languages=sorted(([n, s, c] for n, (s, c) in langs.items()), key=lambda l: -l[1]),
        updated=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )


def load_stats():
    cache = ASSETS / "stats.json"
    try:
        st = fetch_stats()
        cache.write_text(json.dumps(st, indent=1))
    except Exception as e:  # keep rendering from the last good snapshot
        print(f"warning: GitHub API unavailable ({e}); using {cache.name}")
        st = json.loads(cache.read_text())
    counts = [c for _, c in st["days"]]
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    current = 0
    for c in reversed(counts[:-1] if counts and not counts[-1] else counts):
        if not c:
            break
        current += 1
    st["longest"], st["current"] = longest, current
    return st


def uptime(today=None):
    today = today or dt.date.today()
    months = (today.year - BIRTH.year) * 12 + today.month - BIRTH.month - (today.day < BIRTH.day)
    return f"{months // 12} years, {months % 12} months"


# ─────────────────── HERO: neofetch session ────────────────────────────────
def hero(st, w=W):
    mobile = w < 600
    fs, lh, pad = (14, 20, 16) if mobile else (15, 21, 24)
    cw = fs * CW
    cols = int((w - 2 * pad) / cw)
    X = lambda col: pad + col * cw

    rows = [
        ("title", "", ""),
        ("row", ". OS:",                    "macOS, Linux, Windows"),
        ("row", ". Host:",                  "MacBook Air (M1, 2020)"),
        ("row", ". Uptime:",                uptime()),
        ("row", ". Role:",                  "Junior DevOps & Infrastructure Automation"),
        ("row", ". Location:",              "Bogor, Indonesia"),
        ("row", ". Shell:",                 "zsh, bash"),
        ("row", ". IDE:",                   "Antigravity IDE, Vim, Nvim, Lazygit, Arduino IDE"),
        ("sep", "", ""),
        ("row", ". Languages.Programming:", "Bash, TypeScript, Swift"),
        ("row", ". Languages.Config:",      "YAML, Dockerfile"),
        ("row", ". Languages.Real:",        "Indonesian, English"),
        ("sep", "", ""),
        ("row", ". Stack.Infra:",           "Docker, Kubernetes, Vercel, VMs"),
        ("row", ". Stack.Observability:",   "Prometheus, Grafana"),
        ("row", ". Skills.System:",         "Linux SysAdmin, Hardening, Networking"),
        ("row", ". Skills.Process:",        "SDLC & Agile"),
        ("row", ". Hobbies:",               "Larping Linux, Arduino, Agentic AI"),
        ("sep", "", ""),
        ("sect", "- Contact", ""),
        ("row", ". Email:",                 "andrahijati@gmail.com"),
        ("row", ". Discord:",               "legacyy5030"),
        ("row", ". Web:",                   "boredandra.vercel.app"),
        ("row", ". Facebook:",              "web.facebook.com/andra.nugroho.921"),
        ("sep", "", ""),
        ("sect", "- GitHub.Stats", ""),
        ("row", ". Repos | Stars | Followers:", f"{st['repos']} | {st['stars']} | {st['followers']}"),
        ("row", ". Commits | Contributions (1y):", f"{st['commits']:,} | {st['contributions']:,}"),
    ]

    cmd = "neofetch --boring"
    y_cmd = 66
    y = y_cmd + lh * 1.6
    t0, step = 1.9, 0.055
    out = []
    for i, (kind, key, val) in enumerate(rows):
        if kind == "sep":
            y += lh * 0.6
            continue
        delay = f"animation-delay:{t0 + i * step:.2f}s"
        g = []
        if kind == "title":
            g += [T(X(0), y, "andra", fs, C["cyan"], weight="bold"),
                  T(X(5), y, "@", fs, C["text"], weight="bold"),
                  T(X(6), y, "SakamotoMrX", fs, C["cyan"], weight="bold"),
                  T(X(18), y, "─" * (cols - 18), fs, C["dim"])]
        elif kind == "sect":
            g += [T(X(0), y, key, fs, C["bright"], weight="bold"),
                  T(X(len(key) + 1), y, "─" * (cols - len(key) - 1), fs, C["dim"])]
        else:
            g.append(T(X(0), y, key, fs, C["orange"]))
            lead = len(key)
            if lead + len(val) + 2 > cols:  # too narrow: value drops below, wrapped on ", "
                parts, line = [], ""
                for item in val.split(", "):
                    cand = f"{line}, {item}" if line else item
                    if len(cand) + 1 > cols - 3 and line:
                        parts.append(line + ",")
                        cand = item
                    line = cand
                vals, lead = parts + [line], 1
                y += lh
            else:
                vals = [val]
            for j, v in enumerate(vals):
                if j:
                    y += lh
                g.append(T(X(cols), y, v, fs, C["cyan"], anchor="end"))
                n = cols - lead - len(v) - 2
                if n > 0 and len(vals) == 1:
                    g.append(T(X(lead + 1), y, "." * n, fs, C["dim"]))
        out.append(f'<g class="r" style="{delay}">{"".join(g)}</g>')
        y += lh

    # neofetch colour blocks
    y += lh * 0.5
    t_end = t0 + len(rows) * step + 0.1
    blocks = ["#484f58", "#f85149", "#3fb950", "#d29922", "#58a6ff", "#d2a8ff", "#39c5cf", "#e6edf3"]
    out.append(f'<g class="r" style="animation-delay:{t_end:.2f}s">' + "".join(
        f'<rect x="{X(i * 4):.1f}" y="{y - 13}" width="{cw * 3.6:.1f}" height="16" rx="2" fill="{c}"/>'
        for i, c in enumerate(blocks)) + "</g>")
    y += lh * 1.8

    # final prompt with blinking cursor
    t_end += 0.25
    out.append(
        f'<g class="r" style="animation-delay:{t_end:.2f}s">'
        + T(X(0), y, "➜", fs, C["green"], weight="bold") + T(X(2), y, "~", fs, C["cyan"], weight="bold")
        + f'<rect class="cur" style="animation-delay:{t_end:.2f}s" x="{X(4):.1f}" y="{y - 13}" width="{cw:.1f}" height="17" fill="{C["text"]}"/></g>')
    H = int(y + 30)

    # the typed command: a cover slides off it one character at a time
    type_css = (
        f".cover{{transform:translateX({len(cmd) * cw:.1f}px);"
        f"animation:type 1.1s steps({len(cmd)}) .5s backwards}}"
        f"@keyframes type{{from{{transform:translateX(0)}}}}"
        f".tcur{{transform:translateX({len(cmd) * cw:.1f}px);opacity:0;"
        f"animation:type 1.1s steps({len(cmd)}) .5s backwards,gone .1s 1.7s backwards}}"
        f"@keyframes gone{{from{{opacity:1}}}}"
    )
    prompt = (
        T(X(0), y_cmd, "➜", fs, C["green"], weight="bold")
        + T(X(2), y_cmd, "~", fs, C["cyan"], weight="bold")
        + T(X(4), y_cmd, cmd, fs, C["bright"])
        + f'<rect class="cover" x="{X(4):.1f}" y="{y_cmd - 15}" width="{len(cmd) * cw + 2:.1f}" height="20" fill="{C["bg"]}"/>'
        + f'<rect class="tcur" x="{X(4):.1f}" y="{y_cmd - 13}" width="{cw:.1f}" height="17" fill="{C["text"]}"/>'
    )

    css = (
        ".r{animation:rin .35s ease-out backwards}"
        "@keyframes rin{from{opacity:0;transform:translateX(-8px)}}"
        ".cur{animation:blink 1.05s step-end infinite}"
        "@keyframes blink{50%{opacity:0}}"
        f".scan{{transform:translateY({H + 120}px);animation:scan 6s linear 3.5s infinite backwards}}"
        "@keyframes scan{from{transform:translateY(0)}}"
        + type_css
    )
    wdefs, wbody = window(w, H, "andra@SakamotoMrX — zsh" if mobile else "andra@SakamotoMrX — zsh — ssh")
    defs = wdefs + (
        '<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#58a6ff" stop-opacity="0"/>'
        '<stop offset=".9" stop-color="#58a6ff" stop-opacity=".05"/>'
        '<stop offset="1" stop-color="#58a6ff" stop-opacity=".12"/></linearGradient>'
    )
    body = (wbody + prompt + "".join(out)
            + f'<rect class="scan" y="-120" width="{w}" height="120" fill="url(#sg)"/>'
            + border(w, H))
    return svg(w, H, "andra@SakamotoMrX neofetch", css, body, defs)


# ─────────────────── PIPELINE: looping deploy ──────────────────────────────
def pipeline(st, w=W):
    """Horizontal on desktop; on mobile the stages stack vertically."""
    mobile = w < 600
    stages = [
        ("commit",  "git",           "git push",        "pushing a8f3c1e → main"),
        ("build",   "githubactions", "actions",         "building on ubuntu-latest"),
        ("test",    "gnubash",       "bash -euo",       "set -euo pipefail && ./test.sh"),
        ("preview", "vercel",        "vercel deploy",   "preview ready → review the URL before prod"),
        ("package", "docker",        "docker build",    "docker build -t andra/app:latest ."),
        ("release", "kubernetes",    "kubectl rollout", "kubectl rollout status deploy/app -n prod"),
    ]
    n = len(stages)
    y0 = 52 if mobile else 58
    if mobile:
        margin, bh, gap = 16, 52, 16
        bw = w - 2 * margin
        xs = [margin] * n
        ys = [y0 + i * (bh + gap) for i in range(n)]
        cx = [margin + 24] * n
        cy = [y + bh / 2 for y in ys]
    else:
        margin, bw, bh = 28, 128, 86
        gap = (w - 2 * margin - n * bw) / (n - 1)
        xs = [margin + i * (bw + gap) for i in range(n)]
        ys = [y0] * n
        cx = [x + bw / 2 for x in xs]
        cy = [y0 + bh / 2] * n
    cyc, run = 10.5, 0.9
    starts = [0.5 + i * 1.4 for i in range(n)]
    ends = [s + run for s in starts]
    done, hold = ends[-1], cyc - 0.5
    p = lambda t: pct(t, cyc)
    rng = random.Random(7)

    css = [
        f".lp{{animation-duration:{cyc}s;animation-iteration-count:infinite;animation-timing-function:linear}}",
        ".spin{transform-box:fill-box;transform-origin:center;animation:spin .8s linear infinite}",
        "@keyframes spin{to{transform:rotate(360deg)}}",
    ]
    body = []

    # connectors, then the packet that zips between nodes (drawn under them)
    for i in range(n - 1):
        css.append(f"@keyframes c{i}{{0%,{p(starts[i + 1])}{{stroke:{C['line']}}}"
                   f"{p(starts[i + 1] + .05)},{p(hold)}{{stroke:{C['green']}}}100%{{stroke:{C['line']}}}}}")
        seg = (f"M{cx[i]} {ys[i] + bh}V{ys[i + 1]}" if mobile else f"M{xs[i] + bw:.1f} {cy[i]}H{xs[i + 1]:.1f}")
        body.append(f'<path class="lp" style="animation-name:c{i}" d="{seg}" '
                    f'stroke="{C["green"]}" stroke-width="2" stroke-dasharray="4 4"/>')
    frames = [(0, 0)]
    for i in range(n):
        frames += [(starts[i], i), (ends[i], i)]
    frames.append((cyc, n - 1))
    css.append("@keyframes pk{" + "".join(
        f"{p(t)}{{transform:translate({cx[i]:.1f}px,{cy[i]:.1f}px)}}" for t, i in frames) + "}")
    css.append(f"@keyframes pko{{0%,{p(starts[0])}{{opacity:0}}{p(starts[0] + .05)},{p(done)}{{opacity:1}}"
               f"{p(done + .05)},100%{{opacity:0}}}}")
    body.append(f'<g class="lp" style="animation-name:pk,pko;opacity:0">'
                f'<circle r="9" fill="url(#glow)"/><circle r="3" fill="{C["green"]}"/></g>')

    for i, (name, slug, cmd, _) in enumerate(stages):
        x, y, s, e = xs[i], ys[i], starts[i], ends[i]
        css.append(
            f"@keyframes b{i}{{0%,{p(s)}{{stroke:{C['line']}}}{p(s + .05)},{p(e)}{{stroke:{C['yellow']}}}"
            f"{p(e + .05)},{p(hold)}{{stroke:{C['green']}}}100%{{stroke:{C['line']}}}}}"
            f"@keyframes d{i}{{0%,{p(s)}{{fill:{C['dim']}}}{p(s + .05)},{p(e)}{{fill:{C['yellow']}}}"
            f"{p(e + .05)},{p(hold)}{{fill:{C['green']}}}100%{{fill:{C['dim']}}}}}"
            f"@keyframes r{i}{{0%,{p(s)}{{opacity:0}}{p(s + .05)},{p(e)}{{opacity:1}}{p(e + .05)},100%{{opacity:0}}}}"
            f"@keyframes k{i}{{0%,{p(e)}{{opacity:0}}{p(e + .05)},{p(hold)}{{opacity:1}}100%{{opacity:0}}}}"
        )
        secs = f"{rng.randint(2, 19)}s"
        if mobile:
            text = (icon(slug, x + 14, y + 16, 20)
                    + T(x + 46, y + 23, name, 14, C["bright"], weight="bold")
                    + T(x + 46, y + 40, cmd, 11, C["muted"])
                    + T(x + 46 + 17 * 6.6, y + 40, f"job {i + 1}/{n}", 10, C["dim"]))
            dot, done_xy = (x + bw - 20, y + 20), (x + bw - 12, y + 40)
        else:
            text = (icon(slug, x + 14, y + 14, 20)
                    + T(x + 44, y + 30, name, 14, C["bright"], weight="bold")
                    + T(x + 14, y + 55, cmd, 11, C["muted"])
                    + T(x + 14, y + 75, f"job {i + 1}/{n}", 10, C["dim"]))
            dot, done_xy = (x + bw - 18, y + 22), (x + bw - 14, y + 75)
        body.append(
            f'<rect class="lp" style="animation-name:b{i}" x="{x:.1f}" y="{y}" width="{bw}" height="{bh}" rx="8" '
            f'fill="{C["panel"]}" stroke="{C["green"]}" stroke-width="1.5"/>'
            + text
            + f'<circle class="lp" style="animation-name:d{i}" cx="{dot[0]:.1f}" cy="{dot[1]}" r="4.5" fill="{C["green"]}"/>'
            + f'<g class="lp" style="animation-name:r{i};opacity:0"><circle class="spin" cx="{dot[0]:.1f}" cy="{dot[1]}" r="9" '
              f'fill="none" stroke="{C["yellow"]}" stroke-width="1.6" stroke-dasharray="14 43" stroke-linecap="round"/></g>'
            + f'<g class="lp" style="animation-name:k{i}">' + T(*done_xy, f"✓ {secs}", 11, C["green"], anchor="end") + "</g>"
        )

    # deploy log
    ly = ys[-1] + bh + 34
    lfs = 12 if mobile else 13
    body.append(T(margin, ly, "➜", 13, C["green"], weight="bold") + T(margin + 2 * 7.8, ly, "~", 13, C["cyan"], weight="bold")
                + T(margin + 4 * 7.8, ly, "./deploy --prod --boring", 13, C["bright"]))
    ly += 24
    for i, (_, _, _, msg) in enumerate(stages):
        nxt = starts[i + 1] if i + 1 < n else done
        css.append(f"@keyframes m{i}{{0%,{p(starts[i])}{{opacity:0}}{p(starts[i] + .05)},{p(nxt)}{{opacity:1}}"
                   f"{p(nxt + .05)},100%{{opacity:0}}}}")
        body.append(f'<g class="lp" style="animation-name:m{i};opacity:0">'
                    + T(margin, ly, f"[{i + 1}/{n}] {msg}", lfs, C["yellow"]) + "</g>")
    css.append(f"@keyframes mf{{0%,{p(done)}{{opacity:0}}{p(done + .05)},{p(hold)}{{opacity:1}}100%{{opacity:0}}}}")
    body.append('<g class="lp" style="animation-name:mf">'
                + T(margin, ly, "✓ released to prod. nothing broke. still boring." if mobile
                    else "✓ released to prod — nothing broke. the servers stay boring.", lfs, C["green"]) + "</g>")

    H = int(ly + 22)
    wdefs, wbody = window(w, H, f"deploy.yml — run #{st['contributions']}" if mobile
                          else f"deploy.yml — main — run #{st['contributions']}")
    defs = wdefs + ('<radialGradient id="glow"><stop offset="0" stop-color="#3fb950" stop-opacity=".7"/>'
                    '<stop offset="1" stop-color="#3fb950" stop-opacity="0"/></radialGradient>')
    return svg(w, H, "deploy pipeline", "".join(css), wbody + "".join(body) + border(w, H), defs)


# ─────────────────── RACK: tech stack ──────────────────────────────────────
RACKS = [
    ("rack-01", "infra", [
        ("linux",       "Linux",          "sysadmin · hardening"),
        ("archlinux",   "Arch Linux",     "daily driver"),
        ("apple",       "macOS",          "MacBook Air M1"),
        ("gnubash",     "Bash",           "glue for everything"),
        ("yaml",        "YAML",           "configs & pipelines"),
        ("docker",      "Docker",         "containers"),
        ("kubernetes",  "Kubernetes",     "orchestration"),
        ("nginx",       "NGINX",          "reverse proxy"),
        ("cloudflare",  "Cloudflare",     "DNS · edge"),
        ("prometheus",  "Prometheus",     "metrics"),
        ("grafana",     "Grafana",        "dashboards"),
    ]),
    ("rack-02", "dev", [
        ("git",           "Git",          "version control"),
        ("githubactions", "GitHub Actions", "CI/CD"),
        ("vercel",        "Vercel",       "preview deploys"),
        ("nextdotjs",     "Next.js",      "web apps"),
        ("react",         "React",        "UI"),
        ("typescript",    "TypeScript",   "typed JS"),
        ("tailwindcss",   "Tailwind CSS", "styling"),
        ("php",           "PHP",          "company sites"),
        ("swift",         "Swift",        "macOS menu bar apps"),
        ("tauri",         "Tauri",        "desktop apps"),
        ("arduino",       "Arduino",      "hardware tinkering"),
    ]),
]


def rack(st, w=W):
    """Racks side by side on desktop, stacked on mobile."""
    mobile = w < 600
    gutter, rail, uh, ug = (16 if mobile else 25), 18, 34, 5
    rw = w - 2 * gutter if mobile else (w - 3 * gutter) / 2
    units = max(len(u) for _, _, u in RACKS)
    rh = 14 + units * (uh + ug) + 9
    slot = 34 + rh + 16          # label + rack + spacing
    racks_h = slot * len(RACKS) if mobile else slot
    H = racks_h + (40 if mobile else 24)
    rng = random.Random(42)
    body, k = [], 0

    for r, (rid, role, items) in enumerate(RACKS):
        x0 = gutter if mobile else gutter + r * (rw + gutter)
        top = 34 + (r * slot if mobile else 0)
        body.append(T(x0, top - 12, f"{rid}", 13, C["muted"], weight="bold")
                    + T(x0 + 9 * 7.8, top - 12, f"· {role}", 13, C["muted"])
                    + T(x0 + rw, top - 12, f"{len(items)}U / 42U", 11, C["muted"], anchor="end"))
        # frame and rails with screw holes
        body.append(f'<rect x="{x0}" y="{top}" width="{rw}" height="{rh}" rx="6" fill="#0b0e13" stroke="{C["line"]}" stroke-width="2"/>')
        for rx_ in (x0 + 4, x0 + rw - rail - 4):
            body.append(f'<rect x="{rx_}" y="{top + 6}" width="{rail}" height="{rh - 12}" rx="2" fill="#151a21"/>')
            for u in range(units * 2):
                body.append(f'<rect x="{rx_ + rail / 2 - 2.5}" y="{top + 14 + u * (uh + ug) / 2 + 6}" width="5" height="5" rx="1" fill="#05070a"/>')
        for i, (slug, name, desc) in enumerate(items):
            ux, uy = x0 + rail + 8, top + 14 + i * (uh + ug)
            uw = rw - 2 * rail - 16
            leds = rw - 2 * rail - 16
            blink = f"animation-duration:{rng.uniform(.25, 1.6):.2f}s;animation-delay:{rng.uniform(0, 2):.2f}s"
            vents = "" if mobile else "".join(
                f'<rect x="{ux + uw - 92 + v * 7}" y="{uy + 9}" width="3" height="{uh - 18}" rx="1" fill="#0b0e13"/>' for v in range(7))
            body.append(
                f'<g class="u" style="animation-delay:{.15 + k * .06:.2f}s">'
                f'<rect x="{ux}" y="{uy}" width="{uw}" height="{uh}" rx="3" fill="{C["face"]}" stroke="#2a313b"/>'
                f'<rect x="{ux + 6}" y="{uy + 5}" width="{uh - 10}" height="{uh - 10}" rx="4" fill="#0d1117"/>'
                + icon(slug, ux + 10, uy + 9, uh - 18)
                + T(ux + uh + 6, uy + 21.5, name, 13, C["bright"], weight="bold")
                + T(ux + uh + 6 + (15 if mobile else 17) * 7.8, uy + 21.5, desc, 11, C["muted"])
                + vents
                + f'<circle cx="{ux + leds - 28}" cy="{uy + uh / 2}" r="3" fill="{C["green"]}"/>'
                + f'<circle class="led" style="{blink}" cx="{ux + leds - 16}" cy="{uy + uh / 2}" r="3" fill="#{BRAND[slug] if BRAND[slug] != "E6EDF3" else "58A6FF"}"/>'
                + "</g>")
            k += 1

    fy = racks_h + 8
    total = sum(len(u) for _, _, u in RACKS)
    body.append(f'<circle class="pulse" cx="{gutter + 5}" cy="{fy - 4}" r="4" fill="{C["green"]}"/>'
                + T(gutter + 16, fy, f"{total}/{total} units healthy · load 42% · 24°C" if mobile
                    else f"PDU-A 230V · load 42% · inlet 24°C · {total}/{total} units healthy", 12, C["muted"]))
    body.append(T(gutter + 16, fy + 20, f"uptime {uptime()}", 12, C["muted"]) if mobile
                else T(w - gutter, fy, f"uptime {uptime()}", 12, C["muted"], anchor="end"))
    css = (
        ".u{animation:uin .55s cubic-bezier(.2,.8,.2,1) backwards}"
        "@keyframes uin{from{opacity:0;transform:translateX(40px)}}"
        ".led{animation-name:led;animation-iteration-count:infinite;animation-timing-function:steps(1)}"
        "@keyframes led{0%{opacity:1}50%{opacity:.15}}"
        ".pulse{animation:pulse 2s ease-in-out infinite}"
        "@keyframes pulse{50%{opacity:.25}}"
    )
    return svg(w, int(H), "tech stack server rack", css, "".join(body))


# ─────────────────── TELEMETRY: Grafana-style panel ────────────────────────
G = dict(bg="#111217", panel="#181b1f", line="#2c3235", text="#ccccdc", muted="#8e8ea0",
         green="#73bf69", blue="#5794f2", purple="#b877d9", orange="#ff9830", cell="#22252b")


_clip_ids = itertools.count()


def odometer(cx, by, value, fs, color, delay):
    """Number whose digits roll into place like a mechanical counter."""
    s = f"{value:,}"
    cw, hc = fs * CW, fs * 1.18
    x = cx - len(s) * cw / 2
    out = []
    for j, ch in enumerate(s):
        if not ch.isdigit():
            out.append(T(x + j * cw, by, ch, fs, color, weight="bold"))
            continue
        d, cid = int(ch), f"oc{next(_clip_ids)}"
        strip = "".join(T(x + j * cw, by + k * hc, str(k % 10), fs, color, weight="bold") for k in range(20))
        out.append(
            f'<g clip-path="url(#{cid})">'
            f'<g class="odo" style="transform:translateY({-(10 + d) * hc:.1f}px);animation-delay:{delay + j * .12:.2f}s">{strip}</g></g>'
            f'<clipPath id="{cid}"><rect x="{x + j * cw:.1f}" y="{by - fs * .95:.1f}" width="{cw:.1f}" height="{hc:.1f}"/></clipPath>'
        )
    return "".join(out)


def telemetry(st, w=W):
    mobile = w < 600
    body, css = [], []
    body.append(icon("grafana", 16, 12, 16, "#F46800")
                + T(42, 25, "andra / github-telemetry" if mobile
                    else "Home  ›  Dashboards  ›  andra / github-telemetry", 12, G["text"])
                + T(w - 16, 25, "⟳ 24h" if mobile else "Last 1 year   ⟳ 24h", 12, G["muted"], anchor="end"))

    def panel(x, y, w, h, title):
        return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="4" fill="{G["panel"]}" stroke="{G["line"]}"/>'
                + T(x + 12, y + 21, title, 12, G["text"]))

    # row 1: stat panels
    y1, ph, m, g = 44, 108, 12, 10
    per_row = 2 if mobile else 4
    pw = (w - 2 * m - (per_row - 1) * g) / per_row
    stats = [
        ("Contributions · 1y", st["contributions"], G["green"], "last 365 days"),
        ("Commits · 1y",       st["commits"],       G["blue"],  f"{st['commits'] / 52:.1f} / week avg"),
        ("Longest streak",     st["longest"],       G["orange"], f"current: {st['current']} days"),
        ("Public repos",       st["repos"],         G["purple"], f"★ {st['stars']}  ·  {st['followers']} followers"),
    ]
    weekly = [sum(c for _, c in st["days"][i:i + 7]) for i in range(0, len(st["days"]), 7)]
    for i, (title, val, col, sub) in enumerate(stats):
        x, y1 = m + i % per_row * (pw + g), 44 + i // per_row * (ph + g)
        body.append(panel(x, y1, pw, ph, title))
        if i == 0:  # sparkline behind the number, like Grafana's stat graph mode
            mx = max(weekly) or 1
            pts = [(x + 1 + j * (pw - 2) / (len(weekly) - 1), y1 + ph - 2 - v / mx * 40) for j, v in enumerate(weekly)]
            line = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
            body.append(f'<polygon class="fade" points="{x + 1:.1f},{y1 + ph - 2} {line} {x + pw - 1:.1f},{y1 + ph - 2}" fill="{col}" fill-opacity=".14"/>'
                        f'<polyline class="draw" pathLength="1" points="{line}" fill="none" stroke="{col}" stroke-width="1.5" stroke-opacity=".7"/>')
        body.append(odometer(x + pw / 2, y1 + 66, val, 34, col, .3 + i * .15))
        body.append(T(x + pw / 2, y1 + 88, sub, 11, G["muted"], anchor="middle"))

    # row 2: time series
    y2, h2 = y1 + ph + g, 220
    tw = w - 2 * m if mobile else 600
    tx = m
    body.append(panel(tx, y2, tw, h2, "contributions / day · last 60 days"))
    days = st["days"][-60:]
    vals = [c for _, c in days]
    mx = max(vals) or 1
    top_ = 10 ** len(str(mx)) // 10
    ymax = -(-mx // top_) * top_ if top_ else mx
    px0, px1, py0, py1 = tx + 44, tx + tw - 16, y2 + 38, y2 + h2 - 30
    for j in range(5):
        gy = py1 - j * (py1 - py0) / 4
        body.append(f'<path d="M{px0} {gy:.1f}H{px1}" stroke="{G["line"]}" stroke-dasharray="2 3"/>'
                    + T(px0 - 8, gy + 4, f"{round(ymax * j / 4)}", 10, G["muted"], anchor="end"))
    for j in (0, 20, 40, 59):
        lx = px0 + j * (px1 - px0) / (len(vals) - 1)
        body.append(T(lx, py1 + 18, days[j][0][5:], 10, G["muted"], anchor="middle"))
    pts = [(px0 + j * (px1 - px0) / (len(vals) - 1), py1 - v / ymax * (py1 - py0)) for j, v in enumerate(vals)]
    line = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    body.append(f'<polygon class="fade" points="{px0},{py1} {line} {px1},{py1}" fill="url(#ag)"/>'
                f'<polyline class="draw" pathLength="1" points="{line}" fill="none" stroke="{G["green"]}" stroke-width="2" stroke-linejoin="round"/>'
                f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.5" fill="{G["green"]}"/>'
                f'<circle class="ping" cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.5" fill="none" stroke="{G["green"]}" stroke-width="1.5"/>')
    peak = max(range(len(vals)), key=vals.__getitem__)
    body.append(f'<g class="fade">' + T(pts[peak][0] + 6, pts[peak][1] + 4, f"peak {vals[peak]}", 10, G["text"]) + "</g>")

    # row 2: languages, as a retro LCD bar gauge
    lx, ly = (m, y2 + h2 + g) if mobile else (tx + tw + g, y2)
    lw = w - m - lx
    body.append(panel(lx, ly, lw, h2, "languages · bytes in public repos"))
    langs = st["languages"][:5]
    total = sum(s for _, s, _ in st["languages"]) or 1
    cells, cg = 28, 2
    cwid = (lw - 24 - (cells - 1) * cg) / cells
    for r, (name, size, col) in enumerate(langs):
        share = size / total * 100
        ry = ly + 50 + r * 34
        body.append(T(lx + 12, ry, name, 12, G["text"]) + T(lx + lw - 12, ry, f"{share:.1f}%", 12, col, anchor="end"))
        lit = max(1, round(share / 100 * cells))
        for c in range(cells):
            cx_ = lx + 12 + c * (cwid + cg)
            if c < lit:
                body.append(f'<rect class="cell" style="animation-delay:{.6 + r * .12 + c * .035:.2f}s" x="{cx_:.1f}" y="{ry + 7}" width="{cwid:.1f}" height="9" rx="1" fill="{col}"/>')
            else:
                body.append(f'<rect x="{cx_:.1f}" y="{ry + 7}" width="{cwid:.1f}" height="9" rx="1" fill="{G["cell"]}"/>')

    H = ly + h2 + 30
    body.insert(0, f'<rect width="{w}" height="{H}" rx="10" fill="{G["bg"]}"/>')
    body.append(T(m, H - 12, f"updated {st['updated']} · GitHub GraphQL API" if mobile
                  else f"updated {st['updated']} · source: GitHub GraphQL API · refreshed daily by GitHub Actions", 10, G["muted"]))

    css = (
        ".odo{animation:odo 1.6s cubic-bezier(.15,.85,.25,1) backwards}"
        "@keyframes odo{from{transform:translateY(0)}}"
        ".draw{stroke-dasharray:1;animation:draw 2.4s ease-out .5s backwards}"
        "@keyframes draw{from{stroke-dashoffset:1}}"
        ".fade{animation:fade 1.2s ease-out 1.6s backwards}"
        "@keyframes fade{from{opacity:0}}"
        ".cell{animation:cell .25s ease-out backwards}"
        "@keyframes cell{from{opacity:.08}}"
        ".ping{transform-box:fill-box;transform-origin:center;opacity:0;animation:ping 1.8s ease-out 2.6s infinite}"
        "@keyframes ping{from{opacity:.9;transform:scale(1)}to{opacity:0;transform:scale(3.5)}}"
    )
    defs = (f'<linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G["green"]}" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="{G["green"]}" stop-opacity="0"/></linearGradient>')
    return svg(w, H, "GitHub telemetry dashboard", css, "".join(body), defs)


# ─────────────────── MAIN ──────────────────────────────────────────────────
if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    st = load_stats()
    for name, fn in (("hero", hero), ("pipeline", pipeline), ("rack", rack), ("telemetry", telemetry)):
        for suffix, w in (("", W), ("-mobile", W_MOBILE)):
            out = fn(st, w)
            (ASSETS / f"{name}{suffix}.svg").write_text(out, encoding="utf-8")
            print(f"assets/{name}{suffix}.svg  {len(out) / 1024:.1f} KB")
