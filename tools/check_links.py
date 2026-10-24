"""모든 HTML의 src·href·srcset·CSS url()이 가리키는 파일이 있는지, img에 alt가 있는지 확인한다.

사용: python tools/check_links.py      (사이트 폴더 어디서 실행해도 됨)
바깥 주소(http·mailto)는 목록만 보여 주고 접속하지 않는다.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

SITE = Path(__file__).resolve().parent.parent


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


def main():
    bad, external = [], set()
    pages = sorted(SITE.rglob("*.html"))
    for page in pages:
        c = Collect()
        c.feed(page.read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    main()
