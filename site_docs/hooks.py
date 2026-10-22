"""Small, deterministic MkDocs output hooks for the Brazilian Portuguese site."""

from pathlib import Path


def on_post_page(output, *, page, config):
    """Emit the complete locale without changing the theme's translation catalog."""
    del page, config
    return output.replace('<html lang="pt" class="no-js">', '<html lang="pt-BR" class="no-js">', 1)


def on_post_build(config):
    """Apply the complete locale to generated utility pages such as 404.html."""
    site_dir = Path(config.site_dir)
    for path in site_dir.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        updated = text.replace('<html lang="pt" class="no-js">', '<html lang="pt-BR" class="no-js">', 1)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
