import re
from markdownify import markdownify as md

def html_to_markdown(html: str) -> str:
    markdown = md(html, heading_style="ATX")

    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    return markdown.strip()
