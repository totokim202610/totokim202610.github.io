# 정 · 뿅 소개 사이트

두 안드로이드 앱 **정 - 캘린더&다이어리&가계부**와 **뿅 - 할일관리**를 소개하는 정적 웹사이트예요.
GitHub Pages(계정 `totokim202610`, 저장소 `totokim202610.github.io`)에 올려 `https://totokim202610.github.io/`에서 봐요.
예전 주소 `https://urstory.github.io/toto-apps/`(저장소 urstory/toto-apps)는 손대지 않고 그대로 둬요.

- 바닐라 HTML/CSS + 아주 작은 JS(갤러리 좌우 단추) — 빌드 없음, 외부 라이브러리 없음
- 글꼴: Google Fonts의 Noto Sans KR(본문)·Jua(제목, 앱과 같은 글꼴)·Gaegu(손글씨 한 줄), 못 불러오면 시스템 한글 글꼴
- 색: 두 앱 `lib/design/palette.dart`의 복숭아 테마 토큰, 어두운 모드는 코코아밤/밤 테마
- 모든 경로가 상대 경로라 루트(`/`)와 하위 경로(`/toto-apps/`) 어디서나 그대로 동작해요
- 베타(비공개) 테스트 중이라 "지금은 베타 테스트 중이에요 — 테스터만 받을 수 있어요" 안내와 Google Play QR(컴퓨터에서만 보임)이 있어요. 정식 출시 뒤 받기 단추로 바꾼다

## 폴더

```
index.html            첫 화면: 두 앱 나란히
jeong/index.html      정 소개
ppyong/index.html     뿅 소개
notes/index.html      소식과 팁 목록(새 글은 맨 위에)
notes/<글>/index.html 소식과 팁 글 하나 = 폴더 하나(영어 kebab-case), 그림은 assets/notes/<글>/
jeong/privacy/        정 개인정보처리방침(사본)
ppyong/privacy/       뿅 개인정보처리방침(사본)
assets/site.css       공통 스타일(색 토큰·라이트/다크)
assets/site.js        갤러리 좌우 단추
assets/jeong/         정 그림(phone/ 8장, tablet/ 3장, 아이콘, 피처 그래픽, chars/ 캐릭터)
assets/ppyong/        뿅 그림(같은 구성)
sitemap.xml           검색 엔진용 페이지 목록(페이지를 더하거나 고치면 <loc>·<lastmod>도 고쳐요)
robots.txt            모두 허용 + sitemap 주소
googledd2337cf31b412ab.html  Google Search Console 소유권 확인(지우지 않아요)
tools/build_assets.py 앱 저장소에서 그림을 웹용으로 다시 만드는 스크립트
tools/build_notes.py  소식과 팁 목록(첫 화면 아래 칸·notes/ 목록·sitemap)을 글 파일에서 다시 만듦
tools/check_links.py  깨진 링크·그림·alt, css·js ?v= 값, 소식과 팁 목록이 맞는지 검사(--fix: ?v= 고침)
```

## 소식과 팁 글 올리기

1. `notes/<영어-kebab>/index.html`을 만든다(앞 글을 복사). `<h1>`, `og:description`, `article:published_time`(YYYY-MM-DD), `og:image`(`https://totokim202610.github.io/assets/notes/<글>/hero.jpg`)는 꼭 채운다. 그림은 `assets/notes/<글>/`에 jpg+webp.
2. `python tools/build_notes.py` — 첫 화면 아래 "소식과 팁" 칸(최신 3편, 맨 위 글은 큰 카드), `notes/` 목록, `sitemap.xml`이 저절로 바뀐다. 이 세 곳의 `<!-- notes:start -->`~`<!-- notes:end -->` 사이는 직접 고치지 않는다.
3. `site.css`·`site.js`를 고쳤다면 `python tools/check_links.py --fix`.
4. `python tools/check_links.py`가 통과해야 올린다. 목록을 안 다시 만들었거나 `?v=`가 옛 값이면 여기서 실패한다.

## 로컬에서 보기

```
python -m http.server 8000
```
브라우저에서 `http://localhost:8000/`을 열어요. 끝나면 Ctrl+C로 서버를 꺼요.

## 그림 다시 만들기

앱의 스토어 스크린샷이나 아이콘이 바뀌면 다시 만들어요. Pillow가 필요해요(`pip install pillow`).

```
python tools/build_assets.py <devel/apps 폴더>
# 예) python tools/build_assets.py C:/Users/ursto/devel/apps
```

- 읽는 곳(앱 저장소는 읽기만 해요)
  - `<앱>/assets-src/store/screenshots/phone/*.png`, `.../tablet/*.png`
  - `<앱>/assets-src/store/play-icon-512.png`, `feature-graphic-1024x500.png`
  - 캐릭터 그림: 스크립트 안 `CHARS` 표에 적힌 스티커·캐릭터 파일
- 만드는 것: 긴 변 1080 이하 PNG(256색) + WebP, 아이콘 192·96·64(파비콘), 피처 그래픽 JPG·WebP(공유 미리보기 `og:image`)
- 스크린샷 파일 이름이 바뀌면 HTML의 `<picture>` 경로와 alt 설명도 같이 고쳐요.
- 다시 만든 뒤 `python tools/check_links.py`로 깨진 곳이 없는지 확인해요.

## 고칠 때 지킬 것

- 앱 화면에 실제로 있는 기능만 써요. 기능 설명은 각 앱의 `docs/STORE.md` 자세한 설명이 원본이에요.
- 다정한 해요체, 과장하지 않기, 다른 제품 이름 쓰지 않기.
- 만든 사람 표시는 **김토토**, 문의는 `toto.kim2026@gmail.com`.
- 스토어에 올라가면 각 앱 페이지의 `.soon` 안내를 실제 Google Play 링크 단추로 바꿔요.
- `og:url`·`og:image`는 공유 미리보기 때문에 절대 주소(`https://totokim202610.github.io/...`)예요. 저장소 이름이나 주소가 바뀌면 같이 고쳐요.
- `assets/site.css`·`site.js`를 고치면 `python tools/check_links.py --fix`로 모든 HTML의 `?v=` 값(파일 내용 해시)을 바꿔요. 안 바꾸면 브라우저가 10분 동안 옛 파일을 써서 새 페이지가 깨져 보여요(검사가 실패해서 알려 줘요).
- 개인정보처리방침 원본은 `jeong-privacy` 저장소(`https://urstory.github.io/jeong-privacy/`, 앱과 Google Play에 등록된 주소)예요. `jeong/privacy/`·`ppyong/privacy/`는 그 사본이라, 원본을 고치면 여기도 똑같이 복사해요.
