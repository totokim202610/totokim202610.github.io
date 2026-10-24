# 정 · 뿅 소개 사이트

두 안드로이드 앱 **정 - 캘린더&다이어리&가계부**와 **뿅 - 할일관리**를 소개하는 정적 웹사이트예요.
GitHub Pages에 올려 `https://urstory.github.io/toto-apps/`에서 보는 것을 기준으로 만들었어요.

- 바닐라 HTML/CSS + 아주 작은 JS(갤러리 좌우 단추) — 빌드 없음, 외부 라이브러리 없음
- 글꼴: Google Fonts의 Noto Sans KR(본문)·Jua(제목, 앱과 같은 글꼴)·Gaegu(손글씨 한 줄), 못 불러오면 시스템 한글 글꼴
- 색: 두 앱 `lib/design/palette.dart`의 복숭아 테마 토큰, 어두운 모드는 코코아밤/밤 테마
- 모든 경로가 상대 경로라 하위 경로(`/toto-apps/`)에서도 그대로 동작해요
- 출시 전이라 스토어 링크는 없고 "곧 Google Play에서 만나요" 안내만 있어요

## 폴더

```
index.html            첫 화면: 두 앱 나란히
jeong/index.html      정 소개
ppyong/index.html     뿅 소개
assets/site.css       공통 스타일(색 토큰·라이트/다크)
assets/site.js        갤러리 좌우 단추
assets/jeong/         정 그림(phone/ 8장, tablet/ 3장, 아이콘, 피처 그래픽, chars/ 캐릭터)
assets/ppyong/        뿅 그림(같은 구성)
tools/build_assets.py 앱 저장소에서 그림을 웹용으로 다시 만드는 스크립트
tools/check_links.py  깨진 링크·그림·alt 검사
```

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
- `og:url`·`og:image`는 공유 미리보기 때문에 절대 주소(`https://urstory.github.io/toto-apps/...`)예요. 저장소 이름이나 주소가 바뀌면 같이 고쳐요.
