"""Keyframe helper for looping multi-step SVG animations.

Every element gets its own @keyframes over one shared period, so a whole
scene plays as a single timeline and loops without drifting.
"""


class Timeline:
    def __init__(self, period: float, prefix: str):
        self.period = period
        self.prefix = prefix
        self.rules: list[str] = []
        self.count = 0

    def pct(self, t: float) -> str:
        return f"{max(0.0, min(100.0, t / self.period * 100)):.3f}%"

    def _name(self) -> str:
        self.count += 1
        return f"{self.prefix}{self.count}"

    def _use(self, name: str, timing: str = "linear") -> str:
        return f"animation:{name} {self.period}s {timing} infinite"

    def appear(self, at: float, fade: float = 0.3, dy: float = 6) -> str:
        """Hidden until `at`, then fades in and stays to the end of the loop."""
        n = self._name()
        self.rules.append(
            f"@keyframes {n}{{0%,{self.pct(at)}{{opacity:0;transform:translateY({dy}px)}}"
            f"{self.pct(at + fade)},100%{{opacity:1;transform:none}}}}"
        )
        return self._use(n)

    def window(self, start: float, end: float, fade: float = 0.45) -> str:
        """Visible between start and end, fading at both edges."""
        n = self._name()
        self.rules.append(
            f"@keyframes {n}{{0%,{self.pct(start)}{{opacity:0}}"
            f"{self.pct(start + fade)},{self.pct(end - fade)}{{opacity:1}}"
            f"{self.pct(end)},100%{{opacity:0}}}}"
        )
        return self._use(n)

    def typed(self, at: float, dur: float, chars: int) -> str:
        """scaleX reveal in `chars` steps, for a clip rect anchored at its left edge."""
        n = self._name()
        self.rules.append(
            f"@keyframes {n}{{0%,{self.pct(at)}{{transform:scaleX(0);animation-timing-function:steps({chars},end)}}"
            f"{self.pct(at + dur)},100%{{transform:scaleX(1)}}}}"
        )
        return self._use(n)

    def draw(self, at: float, dur: float, to: float = 0.0) -> str:
        """Stroke draw for a path with pathLength="1" and stroke-dasharray:1."""
        n = self._name()
        self.rules.append(
            f"@keyframes {n}{{0%,{self.pct(at)}{{stroke-dashoffset:1}}"
            f"{self.pct(at + dur)},100%{{stroke-dashoffset:{to}}}}}"
        )
        return self._use(n, "ease-out")

    def move(self, at: float, dur: float, x0: float, y0: float, x1: float, y1: float) -> str:
        n = self._name()
        self.rules.append(
            f"@keyframes {n}{{0%,{self.pct(at)}{{transform:translate({x0}px,{y0}px)}}"
            f"{self.pct(at + dur)},100%{{transform:translate({x1}px,{y1}px)}}}}"
        )
        return self._use(n, "cubic-bezier(.5,0,.2,1)")

    def grow(self, at: float, dur: float) -> str:
        """scaleX 0 → 1, eased, for progress bars."""
        n = self._name()
        self.rules.append(
            f"@keyframes {n}{{0%,{self.pct(at)}{{transform:scaleX(0)}}"
            f"{self.pct(at + dur)},100%{{transform:scaleX(1)}}}}"
        )
        return self._use(n, "ease-in-out")

    def pulse(self, at: float, dur: float = 0.9) -> str:
        """One expanding ring at `at`."""
        n = self._name()
        self.rules.append(
            f"@keyframes {n}{{0%,{self.pct(at)}{{transform:scale(.4);opacity:0}}"
            f"{self.pct(at + 0.05)}{{opacity:.9}}"
            f"{self.pct(at + dur)},100%{{transform:scale(2.6);opacity:0}}}}"
        )
        return self._use(n, "ease-out")

    def css(self) -> str:
        return "\n".join(self.rules)
