"""Generate assets/icon.ico with stdlib only (no Pillow).

Writes an ICO containing 16/32/48/256 px BMP-encoded 32bpp images: a Claude-orange
rounded square with a white terminal chevron. Run once; the .ico is the artifact.

    python tools/make_icon.py
"""
import struct
from pathlib import Path

SIZES = (16, 32, 48, 256)
BG = (0x1E, 0x1E, 0x1E)        # window/panel dark, used for the corner cutout
ORANGE = (0xD9, 0x77, 0x57)    # Claude accent
WHITE = (0xFF, 0xFF, 0xFF)


def _blank(size):
    """size x size grid of (r, g, b, a) tuples, fully transparent."""
    return [[(0, 0, 0, 0) for _ in range(size)] for _ in range(size)]


def _rounded_square(px, size):
    radius = max(2, round(size * 0.22))
    inset = max(1, round(size * 0.04))
    lo, hi = inset, size - 1 - inset
    for y in range(lo, hi + 1):
        for x in range(lo, hi + 1):
            # distance test only inside the four corner boxes
            cx = lo + radius if x < lo + radius else (hi - radius if x > hi - radius else x)
            cy = lo + radius if y < lo + radius else (hi - radius if y > hi - radius else y)
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius:
                px[y][x] = (*ORANGE, 255)


def _chevron(px, size):
    """A '>' mark: two strokes meeting at a point, centred."""
    t = max(1, round(size * 0.085))          # stroke thickness
    half = round(size * 0.17)                # arm length in each axis
    cx, cy = round(size * 0.44), size // 2
    for i in range(-half, half + 1):
        x = cx + (half - abs(i))
        y = cy + i
        for dy in range(-(t // 2), t // 2 + 1):
            for dx in range(-(t // 2), t // 2 + 1):
                yy, xx = y + dy, x + dx
                if 0 <= yy < size and 0 <= xx < size and px[yy][xx][3]:
                    px[yy][xx] = (*WHITE, 255)
    # underscore to the right of the chevron
    if size >= 32:
        uy = cy + half - t // 2
        for x in range(cx + half + t, min(size - round(size * 0.14), size)):
            for dy in range(t):
                yy = uy + dy
                if 0 <= yy < size and px[yy][x][3]:
                    px[yy][x] = (*WHITE, 255)


def _bmp_image(px, size):
    """BITMAPINFOHEADER + BGRA rows (bottom-up) + AND mask, as ICO expects."""
    header = struct.pack(
        "<IiiHHIIiiII",
        40,            # biSize
        size,          # biWidth
        size * 2,      # biHeight: doubled for XOR+AND masks
        1,             # biPlanes
        32,            # biBitCount
        0, 0, 0, 0, 0, 0,
    )
    body = bytearray()
    for y in range(size - 1, -1, -1):
        for x in range(size):
            r, g, b, a = px[y][x]
            body += bytes((b, g, r, a))
    mask_row = (size + 31) // 32 * 4        # padded to 4 bytes
    body += bytes(mask_row * size)          # all-zero: alpha channel governs
    return header + bytes(body)


def build(out_path: Path):
    images = []
    for size in SIZES:
        px = _blank(size)
        _rounded_square(px, size)
        _chevron(px, size)
        images.append((size, _bmp_image(px, size)))

    offset = 6 + 16 * len(images)
    header = struct.pack("<HHH", 0, 1, len(images))
    entries = bytearray()
    for size, data in images:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset)
        offset += len(data)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as fh:
        fh.write(header)
        fh.write(entries)
        for _size, data in images:
            fh.write(data)
    return out_path


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "assets" / "icon.ico"
    build(target)
    print("wrote", target, target.stat().st_size, "bytes")
