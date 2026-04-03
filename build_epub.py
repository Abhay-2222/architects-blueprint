"""
build_epub.py — Generate The Architect's Blueprint EPUB from markdown sources.
Run from: D:/Someinfo/book/
Output:   D:/Someinfo/book/architects-blueprint.epub

No external dependencies — uses Python stdlib only.
"""

import re
import zipfile
from pathlib import Path
from datetime import datetime

BOOK_DIR = Path(__file__).parent
OUT_FILE = BOOK_DIR / "architects-blueprint.epub"

CHAPTERS = [
    ("ch01-the-city-analogy.md",           "Chapter 1 \u2014 The City Analogy"),
    ("ch02-clients-and-servers.md",         "Chapter 2 \u2014 Clients and Servers"),
    ("ch03-protocols.md",                   "Chapter 3 \u2014 Protocols: The Language of Machines"),
    ("ch04-apis.md",                        "Chapter 4 \u2014 APIs: The Front Door"),
    ("ch05-what-is-a-registry.md",          "Chapter 5 \u2014 What Is a Registry?"),
    ("ch06-the-database.md",                "Chapter 6 \u2014 The Database: Your Filing Cabinet"),
    ("ch07-authentication.md",              "Chapter 7 \u2014 Authentication: The ID Card at the Door"),
    ("ch08-routing.md",                     "Chapter 8 \u2014 Routing: The Postal Sorting Office"),
    ("ch09-validation.md",                  "Chapter 9 \u2014 Validation: The Building Inspector"),
    ("ch10-the-publisher.md",               "Chapter 10 \u2014 The Publisher: How You List Your Tool"),
    ("ch11-what-is-an-ai-agent.md",         "Chapter 11 \u2014 What Is an AI Agent?"),
    ("ch12-tools.md",                       "Chapter 12 \u2014 Tools: The Agent\u2019s Hands"),
    ("ch13-sessions-and-conversations.md",  "Chapter 13 \u2014 Sessions and Conversations"),
    ("ch14-hooks.md",                       "Chapter 14 \u2014 Hooks: Rules the Agent Must Follow"),
    ("ch15-permissions-and-sandboxing.md",  "Chapter 15 \u2014 Permissions and Sandboxing"),
    ("ch16-mcp-client.md",                  "Chapter 16 \u2014 MCP Client: The Agent Calls the Registry"),
    ("ch17-skills.md",                      "Chapter 17 \u2014 Skills: Pre-Packaged Superpowers"),
    ("ch18-docker.md",                      "Chapter 18 \u2014 Docker: Shipping Containers for Code"),
    ("ch19-kubernetes.md",                  "Chapter 19 \u2014 Kubernetes: The Construction Site Foreman"),
    ("ch20-cicd.md",                        "Chapter 20 \u2014 CI/CD: The Factory Assembly Line"),
    ("ch21-monitoring.md",                  "Chapter 21 \u2014 Monitoring: The Control Room Dashboard"),
    ("ch22-what-ai-actually-is.md",         "Chapter 22 \u2014 What AI Actually Is (No Hype)"),
    ("ch23-mcp-how-ai-gets-hands.md",       "Chapter 23 \u2014 MCP: How AI Gets Hands"),
    ("ch24-build-your-own-mcp-server.md",   "Chapter 24 \u2014 Building Your Own MCP Server"),
    ("ch25-home-lab.md",                    "Chapter 25 \u2014 The Home Lab: Your Personal Data Center"),
    ("ch26-smart-home-architecture.md",     "Chapter 26 \u2014 Smart Home Architecture"),
    ("ch27-thinking-like-an-architect.md",  "Chapter 27 \u2014 Thinking Like an Architect"),
    ("ch28-design-before-you-build.md",     "Chapter 28 \u2014 Design It Before You Build It"),
    ("ch29-your-first-architecture.md",     "Chapter 29 \u2014 Putting It All Together: Your First Architecture"),
    ("ch30-product-thinking.md",            "Chapter 30 \u2014 Product Thinking: Seeing Problems as Systems"),
    ("ch31-product-strategy.md",            "Chapter 31 \u2014 Product Strategy: From Idea to Architecture"),
    ("ch32-product-designer.md",            "Chapter 32 \u2014 The Product Designer\u2019s Chapter"),
    ("ch33-teaching-others.md",             "Chapter 33 \u2014 Teaching Others"),
    ("ch34-networking-internals.md",        "Chapter 34 \u2014 Networking Internals"),
    ("ch35-security-and-threat-models.md",  "Chapter 35 \u2014 Security and Threat Models"),
    ("ch36-prompt-engineering-and-rag.md",  "Chapter 36 \u2014 Prompt Engineering and RAG"),
    ("appendix-a-glossary.md",              "Appendix A \u2014 Glossary"),
    ("appendix-b-cheat-sheet.md",           "Appendix B \u2014 Cheat Sheet"),
    ("appendix-c-what-to-learn-next.md",    "Appendix C \u2014 What to Learn Next"),
    ("appendix-d-codebase-map.md",          "Appendix D \u2014 Codebase Map"),
]


# ── XML / HTML helpers ────────────────────────────────────────────────────────

def xe(s: str) -> str:
    """Escape a string for safe use in XML text content and attributes."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


# ── Markdown -> XHTML ─────────────────────────────────────────────────────────

def md_to_xhtml(text: str) -> str:
    """Convert markdown to XHTML-safe HTML for EPUB body content."""
    lines = text.split("\n")
    out = []
    in_code = False
    in_table = False
    in_ul = False
    in_ol = False
    code_buf = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def inline(s: str) -> str:
        """
        Process inline markdown. Strategy:
        1. Split on code spans so we can escape their content separately.
        2. For non-code segments: escape & < > first, then apply bold/italic/links.
           This means raw & < > in prose become &amp; &lt; &gt; (correct XHTML).
        """
        # Split preserving code span delimiters
        parts = re.split(r"(`[^`]+`)", s)
        result = []
        for part in parts:
            if part.startswith("`") and part.endswith("`") and len(part) > 2:
                inner = xe(part[1:-1])
                result.append(f"<code>{inner}</code>")
            else:
                # Escape raw text entities first
                p = part.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                # Bold-italic, bold, italic
                p = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", p)
                p = re.sub(r"\*\*(.+?)\*\*",     r"<strong>\1</strong>", p)
                p = re.sub(r"\*(.+?)\*",          r"<em>\1</em>", p)
                # Links — href content is already entity-safe because xe() was applied to `p`
                # but we need to re-escape quote chars in URLs; simplest: don't xe() the URL
                p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', p)
                result.append(p)
        return "".join(result)

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code blocks
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
                close_lists()
                in_table = False
            else:
                in_code = False
                # Escape the whole code block as plain text
                code_text = xe("\n".join(code_buf))
                out.append(f"<pre><code>{code_text}</code></pre>")
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Blank line
        if not line.strip():
            close_lists()
            if in_table:
                out.append("</tbody></table>")
                in_table = False
            i += 1
            continue

        # Headings
        h_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if h_match:
            close_lists()
            level = len(h_match.group(1))
            heading_text = inline(h_match.group(2))
            out.append(f"<h{level}>{heading_text}</h{level}>")
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            close_lists()
            out.append(f"<blockquote><p>{inline(line[2:])}</p></blockquote>")
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^---+\s*$", line.strip()):
            close_lists()
            out.append("<hr/>")
            i += 1
            continue

        # Table header row (followed by separator on next line)
        if "|" in line:
            if not in_table:
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if re.match(r"^\|[-| :]+\|?\s*$", next_line.strip()):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    headers = "".join(f"<th>{inline(c)}</th>" for c in cells)
                    out.append(f"<table><thead><tr>{headers}</tr></thead><tbody>")
                    in_table = True
                    i += 2  # skip separator
                    continue
            # Body row
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            row = "".join(f"<td>{inline(c)}</td>" for c in cells)
            out.append(f"<tr>{row}</tr>")
            i += 1
            continue

        if in_table:
            out.append("</tbody></table>")
            in_table = False

        # Unordered list
        ul_match = re.match(r"^[-*+]\s+(.+)$", line)
        if ul_match:
            if not in_ul:
                close_lists()
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(ul_match.group(1))}</li>")
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r"^\d+\.\s+(.+)$", line)
        if ol_match:
            if not in_ol:
                close_lists()
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline(ol_match.group(1))}</li>")
            i += 1
            continue

        # Paragraph
        close_lists()
        out.append(f"<p>{inline(line)}</p>")
        i += 1

    close_lists()
    if in_table:
        out.append("</tbody></table>")
    if in_code and code_buf:
        out.append(f"<pre><code>{xe(chr(10).join(code_buf))}</code></pre>")

    return "\n".join(out)


# ── EPUB CSS ──────────────────────────────────────────────────────────────────

EPUB_CSS = """\
@charset "UTF-8";

body {
  font-family: -apple-system, BlinkMacSystemFont, Georgia, serif;
  font-size: 1em;
  line-height: 1.75;
  color: #1a1a1a;
  margin: 1.5em 1.5em;
}

h1, h2, h3, h4 {
  font-family: -apple-system, BlinkMacSystemFont, Helvetica Neue, Helvetica, sans-serif;
  line-height: 1.3;
  margin-top: 2em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

h1 {
  font-size: 1.8em;
  border-bottom: 2px solid #0071e3;
  padding-bottom: 0.3em;
  page-break-before: always;
}

h2 { font-size: 1.25em; }
h3 { font-size: 1.05em; }

p { margin: 0.75em 0; }

code {
  font-family: Menlo, Courier New, monospace;
  font-size: 0.84em;
  background: #f2f2f7;
  padding: 0.1em 0.35em;
  border-radius: 3px;
}

pre {
  background: #1c1c2e;
  color: #e5e5ea;
  padding: 1em 1.1em;
  border-radius: 8px;
  font-size: 0.8em;
  line-height: 1.55;
  margin: 1.25em 0;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

pre code {
  background: none;
  padding: 0;
  font-size: inherit;
  color: inherit;
  border-radius: 0;
}

blockquote {
  border-left: 3px solid #0071e3;
  margin: 1.25em 0;
  padding: 0.5em 1em;
  color: #3a3a3c;
  font-style: italic;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.25em 0;
  font-size: 0.9em;
}

th {
  background: #0071e3;
  color: #ffffff;
  font-weight: 600;
  padding: 0.5em 0.75em;
  text-align: left;
  font-style: normal;
}

td {
  padding: 0.4em 0.75em;
  border-bottom: 1px solid #d1d1d6;
  vertical-align: top;
}

tr:nth-child(even) td { background: #f9f9fb; }

hr {
  border: none;
  border-top: 1px solid #d1d1d6;
  margin: 2em 0;
}

ul, ol {
  margin: 0.75em 0;
  padding-left: 1.5em;
}

li { margin: 0.3em 0; }

a { color: #0071e3; }

strong { font-weight: 600; }
"""


# ── EPUB XML builders ─────────────────────────────────────────────────────────

def make_xhtml(title: str, body_html: str) -> str:
    safe_title = xe(title)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>{safe_title}</title>
  <link rel="stylesheet" type="text/css" href="../css/style.css"/>
</head>
<body>
{body_html}
</body>
</html>"""


def make_opf(chapters_meta: list) -> str:
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest_items = "\n    ".join(
        f'<item id="ch{str(idx+1).zfill(2)}" href="text/ch{str(idx+1).zfill(2)}.xhtml"'
        f' media-type="application/xhtml+xml"/>'
        for idx in range(len(chapters_meta))
    )
    manifest_items += (
        '\n    <item id="css" href="css/style.css" media-type="text/css"/>'
        '\n    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
        '\n    <item id="nav" href="text/nav.xhtml"'
        ' media-type="application/xhtml+xml" properties="nav"/>'
    )

    spine_items = "\n    ".join(
        f'<itemref idref="ch{str(idx+1).zfill(2)}"/>'
        for idx in range(len(chapters_meta))
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">architects-blueprint-2024</dc:identifier>
    <dc:title>The Architect\u2019s Blueprint</dc:title>
    <dc:creator>The Architect\u2019s Blueprint</dc:creator>
    <dc:language>en</dc:language>
    <dc:description>Systems thinking, AI internals, and production infrastructure for curious minds.</dc:description>
    <dc:subject>Computer Science</dc:subject>
    <dc:subject>Artificial Intelligence</dc:subject>
    <meta property="dcterms:modified">{date}</meta>
  </metadata>
  <manifest>
    {manifest_items}
  </manifest>
  <spine toc="ncx">
    {spine_items}
  </spine>
</package>"""


def make_ncx(chapters_meta: list) -> str:
    nav_points = "\n  ".join(
        f'<navPoint id="ch{str(idx+1).zfill(2)}" playOrder="{idx+1}">\n'
        f'    <navLabel><text>{xe(title)}</text></navLabel>\n'
        f'    <content src="text/ch{str(idx+1).zfill(2)}.xhtml"/>\n'
        f'  </navPoint>'
        for idx, (_, title) in enumerate(chapters_meta)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="architects-blueprint-2024"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>The Architect\u2019s Blueprint</text></docTitle>
  <navMap>
  {nav_points}
  </navMap>
</ncx>"""


def make_nav(chapters_meta: list) -> str:
    items = "\n      ".join(
        f'<li><a href="ch{str(idx+1).zfill(2)}.xhtml">{xe(title)}</a></li>'
        for idx, (_, title) in enumerate(chapters_meta)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="en" lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Table of Contents</title>
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
      {items}
    </ol>
  </nav>
</body>
</html>"""


# ── Build ─────────────────────────────────────────────────────────────────────

def build_epub():
    if OUT_FILE.exists():
        OUT_FILE.unlink()

    with zipfile.ZipFile(OUT_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype MUST be first entry and MUST be uncompressed (EPUB spec)
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, "application/epub+zip")

        # META-INF/container.xml
        zf.writestr("META-INF/container.xml",
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<container version="1.0"'
            ' xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            '  <rootfiles>\n'
            '    <rootfile full-path="OEBPS/content.opf"'
            ' media-type="application/oebps-package+xml"/>\n'
            '  </rootfiles>\n'
            '</container>')

        # Stylesheet
        zf.writestr("OEBPS/css/style.css", EPUB_CSS)

        # Chapters
        built = 0
        for idx, (filename, title) in enumerate(CHAPTERS):
            src = BOOK_DIR / filename
            if not src.exists():
                print(f"  SKIP (missing): {filename}")
                continue
            md_text = src.read_text(encoding="utf-8")
            body_html = md_to_xhtml(md_text)
            xhtml = make_xhtml(title, body_html)
            zf.writestr(f"OEBPS/text/ch{str(idx+1).zfill(2)}.xhtml",
                        xhtml.encode("utf-8"))
            built += 1

        # Navigation documents
        zf.writestr("OEBPS/text/nav.xhtml", make_nav(CHAPTERS).encode("utf-8"))
        zf.writestr("OEBPS/toc.ncx",        make_ncx(CHAPTERS).encode("utf-8"))
        zf.writestr("OEBPS/content.opf",    make_opf(CHAPTERS).encode("utf-8"))

    kb = OUT_FILE.stat().st_size // 1024
    print(f"Built {built} chapters -> architects-blueprint.epub  ({kb} KB)")
    print(f"Location: {OUT_FILE}")


if __name__ == "__main__":
    build_epub()
