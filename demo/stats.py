"""A tiny module for the demo workflows to test."""


def mean(xs):
    xs = list(xs)
    if not xs:
        raise ValueError("mean of an empty sequence")
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    if not s:
        raise ValueError("median of an empty sequence")
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2
