# -*- coding: utf-8 -*-
"""Neofetch-style GitHub profile card generator (Andrew6rant-inspired)."""
import html
import os
import json
import datetime
import urllib.request

GITHUB_LOGIN = "nishanroy561"

# ------------------------------------------------------------------ ASCII ART
art = r'''
                                           .^!7??7!^.
                                        .75BB###B#&BG5J7!^:
                                     !JYP&&&&#&&&&#####BG5Y?^
                                :~~?5&@@@&&#&##B#####&&&@&##BJ:
                             .:~Y5PB##&&&&&&#BB#&@@@@@@@@@@@@&P^~!~~:.
                         .~7Y5PB&&####&&@@@&&&&@@@@@@@@@@@@@@@@#BBBBBG555J7~:
                       ^YB&&&&@@&&&####&&@@@@@@@@@@@@@@@@@@@@@@@&&&&&&&&&#GP5?.
                     :J#@@&##&@&&&&#B#&@@@@@@@@@@@@@@@@@@@@@@@@@@&&&&&@@&@@&BP7
                    ^G@@@&##@@@@@&&&&@@@@@@@@@@@@@@@@@@@@@@@@@@@&####&BGB&#&&BP^
                   :G&&&&&&&&@@@@&##&@@@@@@@@@@@&&&&&&#&&&@@@@@@@@&##&#GG&Y5B&P!
                  .5#&&&@@&&@@@@&#&@@@@@@&#BGP5YYJJJ??JJJY5PB#@@@&&#B#&@@&BGGBB!
                  7#&&&@@&&@@@&&&@@@@&#G5J?77!!!!!!!!!!!77??JYPB&@&&&&@@@@@@@@&5^
                 .P&#&@@@@@@@&&&@@@&BPJ77!!!~~~~~~~~~~~!!77???JYP#@@@@@@@@@@&&&#5~
                 :YG#&&@@@@@@@@@@&B5J7!!~~~~~~^^^^^^^~~~!!777??JJYG&@@@@@@@@&&&B?:
                 .7B#&&&@@@@@@@&GY?77!!~~~~~~~^^^^^^^~~~~!!777??JJ5G#@@@@@&&&#5!
                 .J&&##&@@@@@&#PJ?7!!!~~~~~^^^^^^^^^^~~~~!!!777??JY5G#@@@@@&&Y:
                  ^5B&&&@@@&&B5J?77!!~~~~~~^^^^^^^^^^~~~~~!!!77??JYY5B@@@@@@5:
                    ^G&&&@&BPYJ??77!!~~~~^^^^^^^^^^^^~~!!77???JJJJJY5P&@@&&5:
                     ~#&&@G5YJJJJJJJJJJ??7!~~~~^^~~!!?JYPGGGGGGPPP5YYYP&@&B:
                      7&&&5JY5PPGGGBB##BGP5J?77!!7?JYPGB#BP5YJJYYPGGPYYB@&J
                       Y&#YY555YYJJJY5GB#BGP5J?77?JY5PPP5J?7!7??JJY5PPY5&&?
                       :G#YJYYJYYJJYJY5Y5555Y?7!!7?JYJJYYYGBBB55PP5555YY#&~
                        !GJJJY5PPPYB##BJYY???7!~~!7JJ7???7YGGPYGBG5YYJJJPP:
                       .~YJ???JYP5JJYYJ?7777?7!!!!?JJ?!~!77?JJJYYJ????JJ5P?~
                       75J?77777?????77!!!7??7!!!7??J?7!~~~!!!!!!!!!77?JYPG5.
                       !5J?7!!!~~~~~~~~!!77??7!!!7??JJ?7!~~~~~~~~~!!7??JYYYJ:
                       ^???7!!~~~^^~~~~!!7??7!~~~!7?JJ?7!~~~~~~~~~!!7?JYYYJ?.
                       .!???77!~~~^~~~~~!7?7!!~^^~!7???7!~~~~~~~~!!7??JYYJ?7
                        :????77!!~~~~~~~!?JYYJ7777JPP5Y?~~~~~~~!!77??JYYYJJ~
                         !J???77!!~~~~~~!YGBBGGPPGB##BP?!~~~~~!!77??JJYYYY?
                         !JJ??777!!!!~~!!7JJJJ?JJJJYYJ?!!!!~!!!!7???JJYYYJ!
                        .7?????777!77!!777???777777?????77777!!77??JJYYYJ?~
                          ~JJ???7777??????JJ??J?JJJJYYJJ?JJ??7777??JJYYJ.
                          .?J???????JJJY5PP55YY55555PPPPPYJJ??77??JJJJY7
                           ^JJJJJ??JJYYY55Y?77!!!!!77JJYYJJJJ????JJJJYJ.
                            !JJJJJJJYYJJ?JJ?7!!!!!!7?YYJJJJJJJJJJJJJYY^
                             ~YYYYYYYYJJJY55PGGGGGBGGP5YYYYYYYYYYYY5Y:
                              ^JYYYYJJJJJJJYYYYYJJYJJJJYYYJJJYYYY55?.
                               .?5YYJJ?????7777!!!7777?????JJY55PG!
                                !PGPPYJ?????7777777????JJJJYPGGBBG:
                                !5PGBBG5YYYJJ?JJ??JYY5555PGB####BP^
                              .^?YY5PGB##BBBGPP5PPGGBBB##&&&&#BGGPPP?^:..
                           .^?PYYYYYYY5PB########&&&&&&&&&#BGP5PPPPG&&#BGP5?:
                       .^75GB#5JJYYJJJJY5PGB###&&&&&&&##BGP5YY55555P&&&&&@@&BPJ!:
                   .^7YG##&&&&5?JJJJJJ??JJYYPPGBBBBBGGP5YJJJJYY55YY#&&&&&&&&&@@&#P7~^:.
               .^7YG##&&#&&&&&#J??JJJJ???777??JJJJJJ???777??JYYYYYB&&&&&&@@&&&&&&@&&##G5J?7!~^::..
        .^!?JYPG#&&&&&&&#&&&&&&BJ7???????77!!7777777777777?JJJJJ5B&&&&&&@@@@&@&&&&&&&&&&&&&&&##BGGPP'''

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

INFO_FS, INFO_LH, GAP_LH = 14, 19.5, 10
PAD, MID_GAP = 30, 44
ART_SX = 0.82   # horizontal squeeze so the portrait isn't stretched wide

info_ch = INFO_FS * 0.6

# --- info block height drives the whole card height ---
info_h = 0.0
first = True
for r in rows:
    if r[0] == "gap":
        info_h += GAP_LH
    else:
        info_h += 0 if first else INFO_LH
        first = False

content_h = info_h
svg_h = int(content_h + 2 * PAD)

# --- size the ASCII art to FILL the full card height (top to bottom) ---
nrows = len(art_lines)
ART_LH = content_h / nrows          # rows span the entire content height
ART_FS = ART_LH * 0.98              # glyphs nearly touch row-to-row (no gaps)
art_adv = ART_FS * 0.6
art_w = art_cols * art_adv * ART_SX  # on-screen width after horizontal squeeze

art_x = PAD
info_x = art_x + art_w + MID_GAP
info_w = TOTAL * info_ch
svg_w = int(info_x + info_w + PAD)

info_y0 = PAD + INFO_FS

# ---------------------------------------------------------------- art tspans
# rendered inside a <g translate/scale>, so x is 0 and coords are pre-squeeze
art_tspans = []
for i, ln in enumerate(art_lines):
    dy = 0 if i == 0 else ART_LH
    art_tspans.append(
        f'    <tspan xml:space="preserve" x="0" dy="{dy:.2f}">{html.escape(ln)}</tspan>')
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

  <g transform="translate({art_x}, {PAD}) scale({ART_SX}, 1)">
    <text fill="{C['art']}" x="0" y="{ART_FS:.2f}" font-size="{ART_FS:.2f}">
{art_block}
    </text>
  </g>

  <text x="{info_x}" y="{info_y0:.1f}" font-size="{INFO_FS}" xml:space="preserve">
{info_block}
  </text>
</svg>
'''

with open("neofetch.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print(f"wrote neofetch.svg ({svg_w}x{svg_h}); art {len(art_lines)}x{art_cols}, "
      f"stripped {indent} indent cols")
