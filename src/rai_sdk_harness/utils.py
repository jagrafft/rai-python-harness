from __future__ import annotations

from time import localtime, strftime


def formatted_time_now() -> str:
    return strftime("%Y-%m-%dT%H%M%S", localtime())
