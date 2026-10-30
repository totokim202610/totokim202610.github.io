"""모든 HTML의 src·href·srcset·CSS url()이 가리키는 파일이 있는지, img에 alt가 있는지 확인한다.
사이트의 .css·.js 링크에 붙은 ?v= 값이 그 파일 내용과 맞는지도 본다(안 맞으면 브라우저가 옛 파일을 써서 새 페이지가 깨져 보임).

사용: python tools/check_links.py          (사이트 폴더 어디서 실행해도 됨)
      python tools/check_links.py --fix    ?v= 값을 지금 파일 내용에 맞게 모든 HTML에서 고친 뒤 검사
바깥 주소(http·mailto)는 목록만 보여 주고 접속하지 않는다.
"""
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

SITE = Path(__file__).resolve().parent.parent
SITE_URL = "https://totokim202610.github.io/"
# href="../assets/site.css?v=1a2b3c4d" 처럼 사이트 안 .css·.js를 부르는 자리
ASSET_REF = re.compile(r'((?:src|href)="(?![a-z]+:)([^"?#]+\.(?:css|js)))(?:\?v=([^"]*))?"')


def asset_version(path):
    """파일 내용의 짧은 해시. 내용이 바뀌면 값도 바뀐다.
    줄바꿈(CRLF/LF)은 같게 본다 — 윈도우 작업 사본과 GitHub에 올라간 파일이 같은 값을 내야 한다."""
    return hashlib.sha1(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:8]


def fix_versions(pages):
    changed = 0
    for page in pages:
        text = page.read_bytes().decode("utf-8")

        def put(m):
            target = (page.parent / unquote(m.group(2))).resolve()
            return f'{m.group(1)}?v={asset_version(target)}"' if target.exists() else m.group(0)

        new = ASSET_REF.sub(put, text)
        if new != text:
            page.write_bytes(new.encode("utf-8"))
            changed += 1
    print(f"?v= 값 고친 페이지 {changed}개")


class Collect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.no_alt = [], set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("src", "href"):
            if a.get(k):
                self.refs.append(a[k])
        if a.get("srcset"):
            self.refs += [p.strip().split(" ")[0] for p in a["srcset"].split(",")]
        if tag == "img" and "alt" not in a:
            self.no_alt.append(a.get("src"))


def check_seo(page, text, sitemap):
    """검색에 필요한 기본: 제목·설명·대표 주소(canonical)·h1 하나, sitemap과 맞는지."""
    if page.name != "index.html":  # 소유권 확인 파일 같은 것은 빼고
        return []
    rel = page.relative_to(SITE)
    url = SITE_URL + ("" if page.parent == SITE else page.parent.relative_to(SITE).as_posix() + "/")
    out = []
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', text)
    canon = re.search(r'<link rel="canonical" href="([^"]*)"', text)
    if not title or not title.group(1).strip():
        out.append(f"{rel}: <title> 없음")
    if not desc or not (40 <= len(desc.group(1)) <= 160):
        out.append(f"{rel}: meta description 없거나 길이가 40~160자 밖")
    if len(re.findall(r"<h1[\s>]", text)) != 1:
        out.append(f"{rel}: <h1>은 한 페이지에 하나")
    if not canon:
        out.append(f"{rel}: <link rel=\"canonical\"> 없음")
    elif canon.group(1) == url:
        if url not in sitemap:
            out.append(f"{rel}: sitemap.xml에 {url} 없음")
        if 'property="og:url"' not in text or f'property="og:url" content="{url}"' not in text:
            out.append(f"{rel}: og:url이 {url}이 아님")
    elif url in sitemap:  # 다른 주소가 대표인 사본(개인정보처리방침)은 sitemap에 넣지 않는다
        out.append(f"{rel}: 대표 주소가 {canon.group(1)}인데 sitemap에 들어 있음")
    return out


def main():
    bad, external = [], set()
    pages = sorted(SITE.rglob("*.html"))
    if "--fix" in sys.argv:
        fix_versions(pages)
    sitemap = set(re.findall(r"<loc>([^<]+)</loc>", (SITE / "sitemap.xml").read_text(encoding="utf-8")))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        bad += check_seo(page, text, sitemap)
        for m in ASSET_REF.finditer(text):
            target = (page.parent / unquote(m.group(2))).resolve()
            if target.exists() and m.group(3) != asset_version(target):
                bad.append(f"{page.relative_to(SITE)}: {m.group(2)}?v= 값이 파일 내용과 다름 → python tools/check_links.py --fix")
        c = Collect()
        c.feed(text)
        for ref in c.refs:
            u = urlparse(ref)
            if u.scheme in ("http", "https", "mailto"):
                external.add(ref)
                continue
            if ref.startswith("#"):
                if ref[1:] and ref[1:] not in c.ids:
                    bad.append(f"{page.relative_to(SITE)}: 없는 앵커 {ref}")
                continue
            if ref.startswith("/"):
                bad.append(f"{page.relative_to(SITE)}: 절대 경로 {ref} (GitHub Pages 하위 경로에서 깨짐)")
                continue
            target = (page.parent / unquote(u.path)).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                bad.append(f"{page.relative_to(SITE)}: 없음 {ref}")
        for src in c.no_alt:
            bad.append(f"{page.relative_to(SITE)}: alt 없음 {src}")
    for css in SITE.rglob("*.css"):
        for ref in re.findall(r"url\(['\"]?([^'\")]+)", css.read_text(encoding="utf-8")):
            if not ref.startswith(("data:", "http")) and not (css.parent / ref).exists():
                bad.append(f"{css.relative_to(SITE)}: 없음 {ref}")
    print(f"페이지 {len(pages)}개 검사")
    print("바깥 링크(접속 안 함):", *sorted(external), sep="\n  ")
    if bad:
        print("문제:", *bad, sep="\n  ")
        sys.exit(1)
    print("깨진 링크·그림 없음")
    # 다꾸 노트 목록(첫 화면·guide/·sitemap)이 글 파일과 맞는지도 여기서 같이 본다
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_guide
    sys.argv = [sys.argv[0], "--check"]
    if build_guide.main():
        sys.exit(1)


if __name__ == "__main__":
    main()
