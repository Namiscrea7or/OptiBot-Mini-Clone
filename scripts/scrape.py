import os
import json
import hashlib
import re
import requests
from utils import html_to_markdown

BASE_URL = "https://support.optisigns.com/api/v2/help_center/articles.json"
ARTICLES_DIR = "articles"
MANIFEST_FILE = "manifest.json"


def fetch_articles():
    articles = []
    page = 1

    while True:
        url = f"{BASE_URL}?page={page}"
        res = requests.get(url)
        res.raise_for_status()

        data = res.json()
        articles.extend(data["articles"])

        if not data["next_page"]:
            break
        page += 1

    return articles


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        return {}
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def hash_content(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_article(article):
    os.makedirs(ARTICLES_DIR, exist_ok=True)

    slug = slugify(article["title"])
    filepath = f"{ARTICLES_DIR}/{slug}.md"

    content = html_to_markdown(article["body"])

    frontmatter = f"""---
title: {article['title']}
url: {article['html_url']}
updated_at: {article['updated_at']}
---

"""

    full_content = frontmatter + content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath, full_content


def run_scraper():
    articles = fetch_articles()
    manifest = load_manifest()

    added = updated = skipped = 0

    for art in articles:
        filepath, content = save_article(art)
        content_hash = hash_content(content)

        article_id = str(art["id"])
        old = manifest.get(article_id)

        if not old:
            added += 1
        elif old["hash"] != content_hash:
            updated += 1
        else:
            skipped += 1
            continue

        manifest[article_id] = {
            "hash": content_hash,
            "file": filepath,
            "updated_at": art["updated_at"]
        }

    save_manifest(manifest)

    print(f"Added: {added}, Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    run_scraper()
