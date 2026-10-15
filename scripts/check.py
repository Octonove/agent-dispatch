#!/usr/bin/env python3
"""Repository checks for agent-dispatch. Run from anywhere: python3 scripts/check.py

1. Frontmatter: SKILL.md and es/SKILL.md are valid YAML with a valid name and description.
2. EN/ES parity: every English doc has a Spanish twin with the same structure (headings,
   tables, lists, code blocks). For SKILL.md also the same numbered headings, inline code
   and numbers (in prose and in code blocks) in each section, so a rule changed in one
   language fails until the other follows.
3. Links: every relative link, image, anchor and absolute link into this repository resolves
   (Markdown, HTML and the URLs inside code blocks, such as the install commands).
4. Length: SKILL.md stays under the word limit, so loading it does not eat the context.
5. Plugin: the Claude Code marketplace and plugin manifests parse, names match, and each
   plugin loads its root SKILL.md (no skills/ folder or 'skills' key that would hide it).

Needs Python 3.9+ and PyYAML. Exits 1 on any error.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO = "Octonove/agent-dispatch"

SKILL_EN = "SKILL.md"
SKILL_ES = "es/SKILL.md"
# Whole file, frontmatter included. Measured on the Spanish version, the longer one.
MAX_SKILL_WORDS = 1300
# Agent Skills spec (agentskills.io): name and description limits, allowed keys.
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


errors: list[str] = []


def error(path: str, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


# --- Markdown parsing ------------------------------------------------------------------

FENCE_RE = re.compile(r"^(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+")
BULLET_RE = re.compile(r"^\s*[-*+]\s+")
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5:]


def sections(body: str) -> list[dict]:
    """Split a Markdown body into sections, one per heading, with a structural summary."""
    out: list[dict] = []
    cur = {"heading": "(top)", "level": 0, "lines": [], "code": [], "code_text": []}
    in_fence = False
    fence_lines = 0
    for line in body.splitlines():
        if FENCE_RE.match(line.strip()):
            if in_fence:
                cur["code"].append(fence_lines)
            in_fence, fence_lines = not in_fence, 0
            continue
        if in_fence:
            fence_lines += 1
            cur["code_text"].append(line)
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append(cur)
            cur = {"heading": m.group(2), "level": len(m.group(1)), "lines": [], "code": [],
                   "code_text": []}
            continue
        cur["lines"].append(line)
    out.append(cur)
    for sec in out:
        sec["summary"] = summarize(sec)
    return out


def summarize(sec: dict) -> dict:
    tables, rows, cols = [], 0, 0
    numbered = bullets = images = 0
    for line in sec["lines"] + [""]:
        s = line.strip()
        if s.startswith("|"):
            if not TABLE_SEP_RE.match(s):
                rows += 1
                cols = max(cols, s.strip("|").count("|") + 1)
            continue
        if rows:
            tables.append((rows, cols))
            rows, cols = 0, 0
        if NUMBERED_RE.match(line):
            numbered += 1
        elif BULLET_RE.match(line):
            bullets += 1
        images += len(re.findall(r"!\[", line)) + len(re.findall(r"<img\s", line))
    number = re.match(r"^(\d+[a-z]?)[.)]?\s", sec["heading"])
    return {
        "level": sec["level"],
        "number": number.group(1) if number else None,
        "tables (rows, columns)": tables,
        "numbered items": numbered,
        "bullets": bullets,
        "images": images,
        "code blocks (lines each)": sec["code"],
    }


def prose(sec: dict) -> str:
    return "\n".join(sec["lines"])


def inline_code(text: str) -> Counter:
    return Counter(m.group(2).strip() for m in INLINE_CODE_RE.finditer(text))


def numbers(text: str) -> Counter:
    # Numbers outside inline code, digits only: "at most 5 findings", "cap: 1 fix round".
    return Counter(NUMBER_RE.findall(INLINE_CODE_RE.sub(" ", text)))


# --- 1. Frontmatter --------------------------------------------------------------------

def check_frontmatter(rel: str) -> dict | None:
    raw, _ = split_frontmatter(read(rel))
    if raw is None:
        error(rel, "no YAML frontmatter: the file must start with '---' and close it with '---'")
        return None
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        error(rel, f"frontmatter is not valid YAML: {exc}")
        return None
    if not isinstance(data, dict):
        error(rel, "frontmatter must be a YAML mapping")
        return None
    unknown = set(data) - ALLOWED_KEYS
    if unknown:
        error(rel, f"unknown frontmatter keys {sorted(unknown)}; allowed: {sorted(ALLOWED_KEYS)}")
    name, desc = data.get("name"), data.get("description")
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > MAX_NAME:
        error(rel, f"name {name!r} must be lowercase letters, digits and single hyphens, "
                   f"at most {MAX_NAME} characters")
    if not isinstance(desc, str) or not desc.strip():
        error(rel, "description is missing or empty")
    else:
        if len(desc) > MAX_DESCRIPTION:
            error(rel, f"description is {len(desc)} characters; the limit is {MAX_DESCRIPTION}")
        if "<" in desc or ">" in desc:
            error(rel, "description must not contain '<' or '>'")
    return data


# --- 2. EN/ES parity -------------------------------------------------------------------

def doc_pairs() -> list[tuple[str, str]]:
    pairs = [(SKILL_EN, SKILL_ES)]
    english = [ROOT / "README.md"] + sorted((ROOT / "examples").glob("*.md")) \
        + sorted((ROOT / "docs").glob("*.md"))
    for path in english:
        if path.name.endswith(".es.md"):
            continue
        twin = path.with_name(path.name[:-3] + ".es.md")
        rel, rel_twin = str(path.relative_to(ROOT)), str(twin.relative_to(ROOT))
        if twin.exists():
            pairs.append((rel, rel_twin))
        else:
            error(rel, f"no Spanish twin: create {rel_twin}")
    for twin in sorted(ROOT.rglob("*.es.md")):
        if ".git" in twin.parts:
            continue
        en = twin.with_name(twin.name[: -len(".es.md")] + ".md")
        if not en.exists():
            error(str(twin.relative_to(ROOT)), f"no English twin: {en.relative_to(ROOT)}")
    return pairs


def check_parity(en: str, es: str, strict: bool) -> None:
    sec_en = sections(split_frontmatter(read(en))[1])
    sec_es = sections(split_frontmatter(read(es))[1])
    if len(sec_en) != len(sec_es):
        error(es, f"{len(sec_es) - 1} headings vs {len(sec_en) - 1} in {en}: "
                  f"headings EN {[s['heading'] for s in sec_en[1:]]} / "
                  f"ES {[s['heading'] for s in sec_es[1:]]}")
        return
    for a, b in zip(sec_en, sec_es):
        where = f"section '{b['heading']}' (EN '{a['heading']}')"
        for key, val in a["summary"].items():
            if b["summary"][key] != val:
                error(es, f"{where}: {key} is {b['summary'][key]} vs {val} in {en}")
        if not strict:
            continue
        code_a, code_b = inline_code(prose(a)), inline_code(prose(b))
        if code_a != code_b:
            only_en = sorted((code_a - code_b).elements())
            only_es = sorted((code_b - code_a).elements())
            error(es, f"{where}: inline code differs; only in EN {only_en}, only in ES {only_es}")
        num_a = numbers(prose(a) + "\n" + "\n".join(a["code_text"]))
        num_b = numbers(prose(b) + "\n" + "\n".join(b["code_text"]))
        if num_a != num_b:
            error(es, f"{where}: numbers differ; only in EN {sorted((num_a - num_b).elements())}, "
                      f"only in ES {sorted((num_b - num_a).elements())}")


# --- 3. Links --------------------------------------------------------------------------

MD_LINK_RE = re.compile(r"!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_LINK_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")
REF_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.M)
OWN_URL_RE = re.compile(
    rf"https://(?:raw\.githubusercontent\.com/{REPO}/(?:main|HEAD)"
    rf"|github\.com/{REPO}/(?:blob|tree|raw)/main)/([^\s)\"'>`]+)", re.I)


def slug(text: str) -> str:
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)  # keep link text only
    text = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return text.replace(" ", "-")


def anchors(rel: str) -> set[str]:
    seen: Counter = Counter()
    out = set()
    for sec in sections(split_frontmatter(read(rel))[1])[1:]:
        base = slug(sec["heading"])
        out.add(base if not seen[base] else f"{base}-{seen[base]}")
        seen[base] += 1
    return out


def check_target(rel: str, target: str) -> None:
    if target.startswith(("http://", "https://", "mailto:")):
        return
    path, _, anchor = target.partition("#")
    dest = (ROOT / rel).parent / path if path else ROOT / rel
    try:
        dest.resolve().relative_to(ROOT)
    except ValueError:
        error(rel, f"link leaves the repository: {target}")
        return
    if not dest.exists():
        error(rel, f"broken link: {target}")
        return
    if anchor and dest.suffix == ".md" and anchor not in anchors(str(dest.resolve().relative_to(ROOT))):
        error(rel, f"broken anchor: {target}")


def check_links(rel: str) -> int:
    text = read(rel)
    count = 0
    for url in OWN_URL_RE.findall(text):  # prose and code blocks: install commands too
        count += 1
        if not (ROOT / url.split("#")[0].split("?")[0]).exists():
            error(rel, f"link into this repository points to a missing file: {url}")
    body = "\n".join(line for sec in sections(text)  # headings can hold links too
                     for line in ([sec["heading"]] if sec["level"] else []) + sec["lines"])
    body = INLINE_CODE_RE.sub(" ", body)
    for target in MD_LINK_RE.findall(body) + HTML_LINK_RE.findall(body) + REF_LINK_RE.findall(body):
        count += 1
        check_target(rel, target)
    return count


# --- 5. Plugin manifests ---------------------------------------------------------------

def load_json(rel: str) -> dict | None:
    try:
        data = json.loads(read(rel))
    except (OSError, json.JSONDecodeError) as exc:
        error(rel, f"not valid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        error(rel, "must be a JSON object")
        return None
    return data


def check_plugins() -> int:
    """Each language ships as a plugin whose root holds the skill: Claude Code loads a plugin
    with SKILL.md at its root, no skills/ folder and no 'skills' key as a single skill."""
    market_rel = ".claude-plugin/marketplace.json"
    if not (ROOT / market_rel).exists():
        error(market_rel, "missing")
        return 0
    market = load_json(market_rel)
    if market is None:
        return 0
    for key in ("name", "owner", "plugins"):
        if key not in market:
            error(market_rel, f"missing '{key}'")
    plugins = market.get("plugins") or []
    shipped = set()
    for entry in plugins:
        name, source = entry.get("name"), entry.get("source")
        if not isinstance(source, str) or not source.startswith("./"):
            error(market_rel, f"plugin {name!r}: expected a relative source such as './es'")
            continue
        base = (ROOT / source).resolve()
        if not base.is_dir():
            error(market_rel, f"plugin {name!r}: source {source} is not a folder")
            continue
        manifest_rel = str((base / ".claude-plugin" / "plugin.json").relative_to(ROOT))
        manifest = load_json(manifest_rel) if (ROOT / manifest_rel).exists() else None
        if manifest is None:
            error(manifest_rel, f"missing or invalid manifest for plugin {name!r}")
            continue
        if manifest.get("name") != name:
            error(manifest_rel, f"name {manifest.get('name')!r} differs from the marketplace entry {name!r}")
        if "skills" in manifest or (base / "skills").exists():
            error(manifest_rel, "a skills/ folder or a 'skills' key stops the root SKILL.md from loading")
        skill_rel = str((base / "SKILL.md").relative_to(ROOT))
        if not (base / "SKILL.md").exists():
            error(manifest_rel, f"plugin {name!r} has no SKILL.md at its root")
        shipped.add(skill_rel)
    for rel in (SKILL_EN, SKILL_ES):
        if rel not in shipped:
            error(market_rel, f"no plugin ships {rel}")
    return len(plugins)


# --- main ------------------------------------------------------------------------------

def main() -> int:
    fm_en, fm_es = check_frontmatter(SKILL_EN), check_frontmatter(SKILL_ES)
    if fm_en and fm_es and fm_en.get("name") != fm_es.get("name"):
        error(SKILL_ES, f"name {fm_es.get('name')!r} differs from {SKILL_EN} ({fm_en.get('name')!r})")
    print("frontmatter  SKILL.md, es/SKILL.md")

    pairs = doc_pairs()
    for en, es in pairs:
        check_parity(en, es, strict=(en == SKILL_EN))
    print(f"parity       {len(pairs)} EN/ES pairs: " + ", ".join(en for en, _ in pairs))

    files = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    links = sum(check_links(rel) for rel in files)
    print(f"links        {links} links checked in {len(files)} Markdown files")

    for rel in (SKILL_EN, SKILL_ES):
        words = len(read(rel).split())
        if words > MAX_SKILL_WORDS:
            error(rel, f"{words} words; the limit is {MAX_SKILL_WORDS}. Move examples out of the skill.")
        print(f"length       {rel}: {words} words (limit {MAX_SKILL_WORDS})")

    print(f"plugins      {check_plugins()} plugins in .claude-plugin/marketplace.json")

    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
