"""Small, deterministic MkDocs output hooks for the Brazilian Portuguese site."""

from html import escape
from pathlib import Path
from urllib.parse import urljoin


def _social_metadata(*, site_url: str, site_name: str, title: str, description: str, url: str) -> str:
    """Return absolute Open Graph and Twitter metadata for a public page."""
    image = urljoin(site_url.rstrip("/") + "/", "assets/og-card.png")
    values = {
        "og:type": "website",
        "og:site_name": site_name,
        "og:title": title,
        "og:description": description,
        "og:url": url,
        "og:image": image,
        "og:image:secure_url": image,
        "og:image:type": "image/png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": "VadeMecum MD — legislação federal brasileira para pessoas e máquinas",
        "og:locale": "pt_BR",
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": image,
        "twitter:image:alt": "VadeMecum MD — legislação federal brasileira para pessoas e máquinas",
    }
    return "\n".join(
        f'<meta property="{escape(key, quote=True)}" content="{escape(value, quote=True)}">'
        if key.startswith("og:")
        else f'<meta name="{escape(key, quote=True)}" content="{escape(value, quote=True)}">'
        for key, value in values.items()
    )


def on_post_page(output, *, page, config):
    """Emit locale and share metadata without changing the theme translations."""
    output = output.replace('<html lang="pt" class="no-js">', '<html lang="pt-BR" class="no-js">', 1)
    if 'property="og:image"' in output:
        return output

    site_url = config.site_url or ""
    title = page.title or config.site_name
    description = page.meta.get("description") or config.site_description
    url = page.canonical_url or site_url
    tags = _social_metadata(
        site_url=site_url,
        site_name=config.site_name,
        title=title,
        description=description,
        url=url,
    )
    return output.replace("</head>", f"{tags}\n</head>", 1)


def on_post_build(config):
    """Apply locale and default share metadata to utility pages such as 404.html."""
    site_dir = Path(config.site_dir)
    for path in site_dir.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        updated = text.replace('<html lang="pt" class="no-js">', '<html lang="pt-BR" class="no-js">', 1)
        if 'property="og:image"' not in updated:
            site_url = config.site_url or ""
            title = f"{config.site_name} — legislação federal brasileira"
            url = urljoin(site_url.rstrip("/") + "/", path.relative_to(site_dir).as_posix())
            tags = _social_metadata(
                site_url=site_url,
                site_name=config.site_name,
                title=title,
                description=config.site_description,
                url=url,
            )
            updated = updated.replace("</head>", f"{tags}\n</head>", 1)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
