from dataclasses import dataclass
from urllib.parse import urlsplit, unquote
from typing import Optional

from utils import CurlError


@dataclass
class URLParts:
    scheme: str
    host: str
    port: int
    path: str
    username: Optional[str] = None
    password: Optional[str] = None


def parse_url(url: str) -> URLParts:
    if "://" not in url:
        url = "http://" + url

    try:
        p = urlsplit(url)

        if p.scheme not in ("http", "https") or not p.hostname:
            raise ValueError

        port = p.port or (443 if p.scheme == "https" else 80)

        path = p.path or "/"

        if p.query:
            path += "?" + p.query

        return URLParts(
            p.scheme,
            p.hostname,
            port,
            path,
            unquote(p.username) if p.username else None,
            unquote(p.password) if p.password else None
        )

    except Exception:
        raise CurlError(3, f"invalid URL: {url}")


def parse_url(url: str) -> URLParts:
    if "://" not in url:
        url = "http://" + url
    try:
        p = urlsplit(url)
        if p.scheme not in ("http", "https") or not p.hostname:
            raise ValueError
        port = p.port or (443 if p.scheme == "https" else 80)
        path = p.path or "/"
        if p.query:
            path += "?" + p.query
        return URLParts(
            p.scheme,
            p.hostname,
            port,
            path,
            unquote(p.username) if p.username else None,
            unquote(p.password) if p.password else None,
        )
    except Exception:
        raise CurlError(3, f"invalid URL: {url}")
