"""Shape text with HarfBuzz and return it as SVG path data, so banners render
crisply on GitHub without relying on web fonts (which its image CSP blocks)."""
import uharfbuzz as hb


class _Pen:
    def __init__(self, sx, ox, oy):
        self.s, self.ox, self.oy, self.d = sx, ox, oy, []

    def _p(self, pt):
        x, y = pt
        return f"{self.ox + x * self.s:.1f} {self.oy - y * self.s:.1f}"

    def moveTo(self, p): self.d.append("M" + self._p(p))
    def lineTo(self, p): self.d.append("L" + self._p(p))
    def qCurveTo(self, c, p): self.d.append("Q" + self._p(c) + " " + self._p(p))
    def curveTo(self, a, b, p): self.d.append("C" + self._p(a) + " " + self._p(b) + " " + self._p(p))
    def closePath(self): self.d.append("Z")


class Face:
    def __init__(self, path, wght=None):
        blob = hb.Blob.from_file_path(path)
        self.face = hb.Face(blob)
        self.font = hb.Font(self.face)
        if wght is not None:
            self.font.set_variations({"wght": wght})
        self.upem = self.face.upem

    def _shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size, tracking=0.0):
        _, pos = self._shape(text)
        s = size / self.upem
        return sum(p.x_advance for p in pos) * s + tracking * size * max(len(pos) - 1, 0)

    def path(self, text, size, x, y, tracking=0.0):
        """Return (d, advance_width). tracking is in em (e.g. -0.03)."""
        infos, pos = self._shape(text)
        s = size / self.upem
        cx, out = x, []
        for i, (info, p) in enumerate(zip(infos, pos)):
            pen = _Pen(s, cx + p.x_offset * s, y - p.y_offset * s)
            self.font.draw_glyph_with_pen(info.codepoint, pen)
            out.extend(pen.d)
            cx += p.x_advance * s + (tracking * size if i < len(infos) - 1 else 0)
        return "".join(out), cx - x
