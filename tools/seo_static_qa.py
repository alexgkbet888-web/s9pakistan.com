from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "s9pakistan.com"
SKIP_DIRS = {".git", "node_modules", "outputs"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.in_title = False
        self.h1_count = 0
        self.description = ""
        self.canonical = ""
        self.links: list[str] = []
        self.json_ld: list[str] = []
        self.in_json_ld = False
        self.json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and values.get("name", "").lower() == "description":
            self.description = values.get("content", "").strip()
        elif tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonical = values.get("href", "").strip()
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"])
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self.in_json_ld = True
            self.json_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_json_ld:
            self.json_ld.append("".join(self.json_parts).strip())
            self.in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json_ld:
            self.json_parts.append(data)


def page_route(file: Path) -> str:
    relative = file.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return f"/{relative[:-10]}"
    return f"/{relative}"


def internal_target_exists(route: str, href: str) -> bool:
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return True
    parsed = urlparse(urljoin(f"https://{DOMAIN}{route}", href))
    if parsed.hostname not in {DOMAIN, f"www.{DOMAIN}"}:
        return True
    relative = unquote(parsed.path).lstrip("/")
    candidates = [ROOT / relative, ROOT / relative / "index.html"]
    return any(candidate.exists() for candidate in candidates)


def main() -> int:
    errors: list[str] = []
    files = [
        file
        for file in ROOT.rglob("*.html")
        if not any(part in SKIP_DIRS for part in file.relative_to(ROOT).parts)
    ]
    for file in files:
        parser = PageParser()
        parser.feed(file.read_text(encoding="utf-8"))
        route = page_route(file)
        title = re.sub(r"\s+", " ", "".join(parser.title_parts)).strip()
        if not title:
            errors.append(f"{route}: missing title")
        if not parser.description:
            errors.append(f"{route}: missing meta description")
        if parser.h1_count != 1:
            errors.append(f"{route}: expected one H1, found {parser.h1_count}")
        if not parser.canonical:
            errors.append(f"{route}: missing canonical")
        for payload in parser.json_ld:
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"{route}: invalid JSON-LD ({exc.msg})")
        for href in parser.links:
            if not internal_target_exists(route, href):
                errors.append(f"{route}: broken internal link {href}")

    print(json.dumps({"pages": len(files), "errors": len(errors)}, indent=2))
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
