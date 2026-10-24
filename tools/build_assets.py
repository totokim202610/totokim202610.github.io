"""앱 저장소의 스토어 자료를 웹용으로 줄여 assets/에 복사한다.

사용: python tools/build_assets.py <devel/apps 폴더 경로>
예)  python tools/build_assets.py C:/Users/ursto/devel/apps
필요: Pillow (pip install pillow)
"""
import sys
from pathlib import Path
from PIL import Image

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "assets"

# (앱, 원본 상대 경로, 출력 이름, 긴 변)
CHARS = {
    "jeong": [
        ("assets/stickers/girl/01-wave.webp", "girl-wave", 360),
        ("assets/stickers/girl/03-hug-peach.webp", "girl-peach", 360),
        ("assets/stickers/girl/05-diary.webp", "girl-diary", 360),
        ("assets/stickers/yomi/02-wagging.webp", "yomi-wag", 360),
        ("assets/stickers/yomi/04-peach.webp", "yomi-peach", 360),
        ("assets/stickers/toto/11-letter.webp", "toto-letter", 240),
        ("assets/stickers/deco/02-heart.webp", "heart", 160),
        ("assets/stickers/deco/08-star.webp", "star", 160),
    ],
    "ppyong": [
        ("assets/characters/girl/smash.webp", "girl-smash", 480),
        ("assets/characters/girl/cheer.webp", "girl-cheer", 360),
        ("assets/characters/yomi/cheer.webp", "yomi-cheer", 360),
        ("assets/monsters/slime.webp", "mon-slime", 200),
        ("assets/monsters/sock.webp", "mon-sock", 200),
        ("assets/monsters/cloud-scared.webp", "mon-cloud", 200),
        ("assets/monsters/paper.webp", "mon-paper", 200),
    ],
}


def save_pair(im: Image.Image, dest: Path, long_side: int, lossy_q=82):
    """긴 변을 줄여 PNG와 WebP를 같이 저장한다."""
    im = im.copy()
    im.thumbnail((long_side, long_side), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")
    png = im if im.mode == "RGBA" else im.convert("RGB")
    # 스크린샷 PNG는 색 수를 줄여 용량을 아낀다(256색, 디더링)
    if im.mode == "RGB":
        png = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    png.save(dest.with_suffix(".png"), optimize=True)
    im.save(dest.with_suffix(".webp"), "WEBP", quality=lossy_q, method=6)
    return im.size


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    apps = Path(sys.argv[1])
    sizes = {}
    for app in ("jeong", "ppyong"):
        src = apps / app / "assets-src" / "store"
        dst = OUT / app
        for kind in ("phone", "tablet"):
            for f in sorted((src / "screenshots" / kind).glob("*.png")):
                s = save_pair(Image.open(f).convert("RGB"), dst / kind / f.stem, 1080)
                sizes[f"{app}/{kind}/{f.stem}"] = s
        icon = Image.open(src / "play-icon-512.png").convert("RGBA")
        save_pair(icon, dst / "icon-192", 192)
        save_pair(icon, dst / "icon-96", 96)
        fav = icon.copy(); fav.thumbnail((64, 64), Image.LANCZOS)
        fav.save(dst / "favicon-64.png", optimize=True)
        fg = Image.open(src / "feature-graphic-1024x500.png").convert("RGB")
        fg.save(dst / "feature-graphic.jpg", "JPEG", quality=86, optimize=True, progressive=True)
        fg.save(dst / "feature-graphic.webp", "WEBP", quality=82, method=6)
        for rel, name, side in CHARS[app]:
            save_pair(Image.open(apps / app / rel).convert("RGBA"), dst / "chars" / name, side)
    for k, v in sizes.items():
        print(k, v)
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"assets 합계 {total/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
