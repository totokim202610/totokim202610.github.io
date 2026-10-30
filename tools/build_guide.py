"""다꾸 노트 글 목록을 글 파일에서 다시 만든다.

글(guide/<이름>/index.html)을 하나 더하거나 고친 뒤 실행하면 세 곳이 같이 바뀐다.
  - guide/index.html  : 모든 글 카드(최신이 위)
  - index.html        : 첫 화면 아래 "다꾸 노트" 칸, 최신 HOME_COUNT편
  - sitemap.xml       : guide/와 글마다 한 줄

글 파일에서 읽는 것: <h1>(카드 제목), og:description(카드 설명), article:published_time(날짜),
og:image(카드 그림 — 같은 이름의 .webp가 있으면 같이 씀).
각 파일의 <!-- guide:start --> … <!-- guide:end --> 사이만 바꾸고 나머지는 건드리지 않는다.

사용: python tools/build_guide.py           만들기
      python tools/build_guide.py --check   바꿀 게 있으면 알리고 종료 코드 1 (check_links.py도 부름)
"""
import html
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
BASE = "https://totokim202610.github.io/"
HOME_COUNT = 3
START, END = "<!-- guide:start -->", "<!-- guide:end -->"
WEEKDAY = "월화수목금토일"


def meta(text, prop):
    m = re.search(rf'<meta (?:property|name)="{re.escape(prop)}" content="([^"]*)"', text)
    return html.unescape(m.group(1)) if m else ""


def read_posts():
    posts = []
    for page in sorted((SITE / "guide").glob("*/index.html")):
        text = page.read_text(encoding="utf-8")
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
        date = meta(text, "article:published_time")
        image = meta(text, "og:image")
        if not (h1 and date and image.startswith(BASE)):
            sys.exit(f"{page.relative_to(SITE)}: <h1>·article:published_time·og:image({BASE}…)가 모두 있어야 해요")
        posts.append({
            "slug": page.parent.name,
            "title": html.unescape(re.sub(r"<[^>]+>", "", h1.group(1)).strip()),
            "desc": meta(text, "og:description"),
            "date": date,
            "image": image[len(BASE):],
        })
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


def korean_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{y}년 {m}월 {d}일"


def card(post, prefix, heading, lazy):
    esc = html.escape
    webp = Path(post["image"]).with_suffix(".webp")
    source = f'<source srcset="{prefix}{webp.as_posix()}" type="image/webp">' if (SITE / webp).exists() else ""
    loading = ' loading="lazy"' if lazy else ""
    return (
        f'        <li>\n'
        f'          <a href="{prefix}guide/{post["slug"]}/">\n'
        f'            <picture>{source}<img src="{prefix}{post["image"]}" alt="" width="1200" height="800"{loading}></picture>\n'
        f'            <div class="txt">\n'
        f'              <{heading}>{esc(post["title"])}</{heading}>\n'
        f'              <p>{esc(post["desc"])}</p>\n'
        f'              <time datetime="{post["date"]}">{korean_date(post["date"])}</time>\n'
        f'            </div>\n'
        f'          </a>\n'
        f'        </li>\n'
    )


def guide_block(posts):
    cards = "".join(card(p, "../", "h2", i > 1) for i, p in enumerate(posts))
    return f'\n      <ul class="guide-list">\n{cards}      </ul>\n      '


def home_block(posts):
    cards = "".join(card(p, "", "h3", True) for p in posts[:HOME_COUNT])
    return (
        '\n  <section class="section home-guide" aria-labelledby="guide-title">\n'
        '    <div class="wrap">\n'
        '      <div class="sec-head">\n'
        '        <span class="eyebrow">매일 하나씩</span>\n'
        '        <h2 id="guide-title">다꾸 노트</h2>\n'
        '        <p>다이어리 꾸미기를 조금 더 즐겁게. 짧은 이야기를 하루에 하나씩 적어요.</p>\n'
        '      </div>\n'
        f'      <ul class="guide-list">\n{cards}      </ul>\n'
        '      <a class="btn btn-ghost all" href="guide/">다꾸 노트 모두 보기 '
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>\n'
        '    </div>\n'
        '  </section>\n  '
    )


def sitemap_block(posts):
    def url(path, date):
        return f"  <url>\n    <loc>{BASE}{path}</loc>\n    <lastmod>{date}</lastmod>\n  </url>\n"
    newest = posts[0]["date"] if posts else ""
    return "\n" + url("guide/", newest) + "".join(url(f'guide/{p["slug"]}/', p["date"]) for p in posts) + "  "


def replace_block(path, block):
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    if text.count(START) != 1 or text.count(END) != 1:
        sys.exit(f"{path.relative_to(SITE)}: {START} … {END} 표시가 한 번씩 있어야 해요")
    head, rest = text.split(START)
    _, tail = rest.split(END)
    new = (head + START + block + END + tail).replace("\n", nl)
    return raw, new


def main():
    check = "--check" in sys.argv
    posts = read_posts()
    stale = []
    for rel, block in (("guide/index.html", guide_block(posts)), ("index.html", home_block(posts)), ("sitemap.xml", sitemap_block(posts))):
        path = SITE / rel
        old, new = replace_block(path, block)
        if old != new:
            stale.append(rel)
            if not check:
                path.write_bytes(new.encode("utf-8"))
    if check:
        if stale:
            print("다꾸 노트 목록이 글과 다름:", ", ".join(stale), "→ python tools/build_guide.py")
            return 1
        print(f"다꾸 노트 목록 맞음(글 {len(posts)}편)")
        return 0
    print(f"글 {len(posts)}편 — 고친 파일: {', '.join(stale) or '없음'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
