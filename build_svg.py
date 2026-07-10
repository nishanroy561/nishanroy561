# -*- coding: utf-8 -*-
"""Neofetch-style GitHub profile card generator (Andrew6rant-inspired)."""
import html
import os
import json
import datetime
import urllib.request

GITHUB_LOGIN = "nishanroy561"

# ------------------------------------------------------------------ ASCII ART
art = r'''                                              .::.
                                           ~YPGBBBPJ7~:.
                                      .:!PG&&&######&#G57.
                                   .^?5G#&@@&#B#&&@@@@@@&5~~~^...
                                ~JPG#&&###&@@&&@@@@@@@@@@@&###BBGY?^
                              ^5&&&&@@&##&@@@@@@@@@@@@@@@@@&&&&@&&#P^
                             ~#@&&&@@@&#&@@@@@@@@@@@@@@@@@@&##&G#GB#J
                            :G&&@&&@@@&&@@@&BGP5YYJJJY5PB&@@##&&&BG#Y
                            J&&@@@@@&&@@&GY?7!~~~~~~!!7??YG&@&@@@@@@#?.
                           .J#&@@@@@@@#PJ7!~~~~^^^^~~!!7??J5#@@@@@&&#7.
                            J&#&@@@@&P?7!!~~~~^^^^^~~~!!7??J5B&@@@&P~
                            ~P&&@@&B5?7!!~~~^^^^^^^^~~~!77?JY5#@@@B^
                              J@@&PYJ??777!!~^^^^^~!?JY5555YYYP&@B^
                               P@GJ5PPPPGBBP5?7!!7J5GBG5JJY5PPYG@J
                               :BPYYYYJJY5PPP5?77?Y55YY5YYY55555&7
                                75JJYP55BGJJ??7~~7J?7??PG5GPYYJYG~
                               :JJ77?JJ?J?7!7?7!!7J?!~!!77??77?J55~
                               :Y?7!!~~~~~!!??!!!7JJ7!~~~~~~!7?JY5!
                               .7?7!!~^^~~!!77~^~!???!~~~~~!!7JYYJ~
                                :???7!~~~~~?Y5J??YPPY!~~~~!77?JYYJ.
                                .?J?77!!~~~?555Y5PP5?!~~!!77?JYYY!
                                .7J??7777777??777????777777??JYY7^
                                 .?J?????JJY5YYYYY5555JJ?77?JJY7
                                  ^JJJ?JJYY5J?!!!!7JYYJJJ??JJYY:
                                   ~JYYYYJJJYYY5Y555YYYYJYYYYY^
                                    ^JYYJJJJJJJJJJJJJJJJJYY5?.
                                     ^PP5J??7777777??JJY5PBP.
                                     ^5PGGP55YJJJY5PPPB###BP!.
                                  .~JJYY5PG####BB##&&&&#GPPPPBPYJ?^
                              .~?5B#5JYJJJY5PB##&&##BG5YY5555&@@@@#GY7:
                          .^75G#&&&&G??JJ?????JYYYYJ????JYYYB@&&&@&@@@#GPY7:
                  .^^!?YPGB&&&&&&&&&&G?????7!!!7777!!77?J?5#@&&&@@&@&&@@@@@&&##BBGGP5J!^.
            .~??5G#&&&&@@@@@@@@&&@&&&@#PJ77!!!!!!!!!!777JG&@&&@@@@@@@@@@@@@@&&&&&@@@@@&&B?.
          :YB&&&@&&&&&@@@@@@@@@&@@@&@&&@&G5J?!~~~~~~~!?P&@@&&@@@@@@@@@@@@@@@@@@@&&&&&@@&@@B?
       .7P#&&&&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&&BPJ77?5#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#7
       :Y5555YY5555555555555555555555555555555555YY55555555555555555555555555555555555555Y:'''

# ------------------------------------------------------- GitHub stats
# Static fallback used when no token is available (e.g. local run without auth).
# When run in CI (or locally with GH_TOKEN set) these are replaced by LIVE data.
STATS = {"Repos": "15", "Commits": "600+", "Stars": "10", "Followers": "40"}


def _gql(query, variables, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "neofetch-readme",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read())
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def fetch_live_stats(login, token):
    base = """
    query($login:String!){
      user(login:$login){
        createdAt
        followers{ totalCount }
        repositories(ownerAffiliations:OWNER, isFork:false, first:100){
          totalCount nodes{ stargazerCount }
        }
      }
    }"""
    u = _gql(base, {"login": login}, token)["user"]
    repos = u["repositories"]["totalCount"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    followers = u["followers"]["totalCount"]

    # lifetime commit contributions, summed year by year via aliases
    start = int(u["createdAt"][:4])
    now = datetime.datetime.utcnow().year
    parts = [
        f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", '
        f'to:"{y}-12-31T23:59:59Z"){{ totalCommitContributions '
        f'restrictedContributionsCount }}'
        for y in range(start, now + 1)
    ]
    cq = "query($login:String!){ user(login:$login){ " + " ".join(parts) + " } }"
    cu = _gql(cq, {"login": login}, token)["user"]
    commits = sum(
        cu[f"y{y}"]["totalCommitContributions"]
        + cu[f"y{y}"]["restrictedContributionsCount"]
        for y in range(start, now + 1)
    )
    return {
        "Repos": f"{repos:,}",
        "Commits": f"{commits:,}",
        "Stars": f"{stars:,}",
        "Followers": f"{followers:,}",
    }


_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if _token:
    try:
        STATS = fetch_live_stats(GITHUB_LOGIN, _token)
        print("fetched LIVE stats:", STATS)
    except Exception as e:  # noqa: BLE001 - fall back to static on any failure
        print("live stats fetch failed, using static fallback:", e)
else:
    print("no token found (GH_TOKEN/GITHUB_TOKEN) - using static STATS")

# ---------------------------------------------------------------- palette
C = {
    "art":   "#d7dae0",  # light gray art (not purple)
    "rule":  "#56b6c2",  # cyan dashes / rules
    "user":  "#98c379",  # green user@host
    "at":    "#abb2bf",
    "label": "#e06c75",  # salmon labels
    "dot":   "#3e4451",  # dim dotted leaders
    "sect":  "#e5c07b",  # yellow section headers
    "green": "#98c379",
    "cyan":  "#56b6c2",
    "yellow":"#e5c07b",
    "blue":  "#61afef",
    "fg":    "#abb2bf",
}

# ---- info rows: ("row", label, value, value_color)
#      ("sect", title)  |  ("user", "nishan", "roy")  |  ("gap",)
TOTAL = 58  # monospace column width for right alignment

rows = [
    ("user", "nishan", "roy"),
    ("gap",),
    ("row", "OS:",     "Windows 11, Android, Linux",             "green"),
    ("row", "Host:",   "Deep Duo Foundation",                    "green"),
    ("row", "Kernel:", "Backend, Distributed Systems, Full-Stack","green"),
    ("row", "Uptime:", "Narula Institute of Technology '27",     "green"),
    ("row", "IDE:",    "VS Code, Claude Code",                   "green"),
    ("gap",),
    ("row", "Languages.Programming:", "Python, TS, JS, Dart, C++","yellow"),
    ("row", "Languages.Real:",        "English, Hindi, Bengali",  "yellow"),
    ("gap",),
    ("row", "Backend:",   "Node.js, Express, FastAPI, Django",   "cyan"),
    ("row", "Frontend:",  "React, Next.js, Tailwind, Flutter",   "cyan"),
    ("row", "Databases:", "PostgreSQL, MongoDB, Redis",          "cyan"),
    ("row", "AI/ML:",     "TensorFlow, LangChain, LangGraph, OpenCV","cyan"),
    ("row", "DevOps:",    "Docker, AWS, Git, n8n",               "cyan"),
    ("gap",),
    ("sect", "Contact"),
    ("row", "Email:",    "nishanroy561@gmail.com",  "blue"),
    ("row", "LinkedIn:", "in/nishanroy",            "blue"),
    ("row", "Website:",  "nishanroy.me",            "blue"),
    ("gap",),
    ("sect", "GitHub Stats"),
    ("row", "Repos:",     STATS["Repos"],     "green"),
    ("row", "Commits:",   STATS["Commits"],   "green"),
    ("row", "Stars:",     STATS["Stars"],     "green"),
    ("row", "Followers:", STATS["Followers"], "green"),
]

# ---------------------------------------------------------------- geometry
art_lines = art.split("\n")
# strip common leading indentation so the face is centered in its own box
indent = min(len(l) - len(l.lstrip(" ")) for l in art_lines if l.strip())
art_lines = [l[indent:] for l in art_lines]
art_cols = max(len(l) for l in art_lines)

ART_FS, ART_LH = 7.2, 7.6
INFO_FS, INFO_LH, GAP_LH = 14, 19.5, 10
PAD, MID_GAP = 30, 44

art_ch = ART_FS * 0.6
info_ch = INFO_FS * 0.6

art_x = PAD
art_w = art_cols * art_ch
info_x = art_x + art_w + MID_GAP
info_w = TOTAL * info_ch
svg_w = int(info_x + info_w + PAD)

art_h = len(art_lines) * ART_LH
# info height
info_h = 0.0
first = True
for r in rows:
    if r[0] == "gap":
        info_h += GAP_LH
    else:
        info_h += 0 if first else INFO_LH
        first = False
content_h = max(art_h, info_h)
svg_h = int(content_h + 2 * PAD)

art_y0 = PAD + (content_h - art_h) / 2 + ART_FS
info_y0 = PAD + (content_h - info_h) / 2 + INFO_FS

# ---------------------------------------------------------------- art tspans
art_tspans = []
for i, ln in enumerate(art_lines):
    dy = 0 if i == 0 else ART_LH
    art_tspans.append(
        f'    <tspan xml:space="preserve" x="{art_x}" dy="{dy:.1f}">{html.escape(ln)}</tspan>')
art_block = "\n".join(art_tspans)

# ---------------------------------------------------------------- info tspans
def esc(s):
    return html.escape(s)

info_tspans = []
first = True
for r in rows:
    if r[0] == "gap":
        info_tspans.append(f'    <tspan x="{info_x}" dy="{GAP_LH}"> </tspan>')
        continue
    dy = 0 if first else INFO_LH
    first = False
    if r[0] == "user":
        _, u, h = r
        dash = "-" * (TOTAL - len(u) - len(h) - 3)
        info_tspans.append(
            f'    <tspan x="{info_x}" dy="{dy:.1f}">'
            f'<tspan fill="{C["user"]}" font-weight="700">{esc(u)}</tspan>'
            f'<tspan fill="{C["at"]}">@</tspan>'
            f'<tspan fill="{C["user"]}" font-weight="700">{esc(h)}</tspan>'
            f'<tspan fill="{C["rule"]}"> {dash}</tspan></tspan>')
    elif r[0] == "sect":
        _, title = r
        dash = "-" * (TOTAL - len(title) - 3)
        info_tspans.append(
            f'    <tspan x="{info_x}" dy="{dy:.1f}">'
            f'<tspan fill="{C["sect"]}" font-weight="700">- {esc(title)} </tspan>'
            f'<tspan fill="{C["rule"]}">{dash}</tspan></tspan>')
    else:
        _, label, value, vc = r
        k = TOTAL - len(label) - len(value) - 2
        if k < 2:
            k = 2
        dots = "." * k
        info_tspans.append(
            f'    <tspan x="{info_x}" dy="{dy:.1f}">'
            f'<tspan fill="{C["label"]}" font-weight="700">{esc(label)}</tspan>'
            f'<tspan fill="{C["dot"]}"> {dots} </tspan>'
            f'<tspan fill="{C[vc]}">{esc(value)}</tspan></tspan>')
info_block = "\n".join(info_tspans)

# ---------------------------------------------------------------- assemble
svg = f'''<svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg" font-family="'JetBrains Mono','Cascadia Code','Fira Code',Consolas,monospace">
  <rect width="{svg_w}" height="{svg_h}" rx="8" fill="#0d1117"/>
  <rect x="0.5" y="0.5" width="{svg_w-1}" height="{svg_h-1}" rx="8" fill="none" stroke="#21262d"/>

  <text fill="{C['art']}" x="{art_x}" y="{art_y0:.1f}" font-size="{ART_FS}">
{art_block}
  </text>

  <text x="{info_x}" y="{info_y0:.1f}" font-size="{INFO_FS}" xml:space="preserve">
{info_block}
  </text>
</svg>
'''

with open("neofetch.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print(f"wrote neofetch.svg ({svg_w}x{svg_h}); art {len(art_lines)}x{art_cols}, "
      f"stripped {indent} indent cols")
