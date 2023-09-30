import re

from markdown import Markdown
from nicegui import ui

HIGHLIGHT_STYLE = "background: #f5f5f5; border-radius: 0.2rem;"
HIGHLIGHT_STYLE += "padding: 0.2rem 0.3rem 0.2rem 0.3rem;"

MATHJAX_SCRIPTS = """
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
"""


def markdown_to_html_with_math(markdown_text: str) -> str:
    md_parser = Markdown(
        extensions=[
            "pymdownx.superfences",
            "pymdownx.highlight",
            "pymdownx.arithmatex",
            "pymdownx.inlinehilite",
        ],
        extension_configs={
            "pymdownx.inlinehilite": {
                "style_plain_text": True,
            },
            "pymdownx.highlight": {
                "guess_lang": False,
                "noclasses": True,
            },
            "pymdownx.arithmatex": {
                "smart_dollar": False,
                "preview": True,
                "generic": True,
            },
        },
    )
    return md_parser.convert(markdown_text)


def apply_tailwind(html: str) -> str:  # Borrowed from NiceGUI's ui.markdown
    rep = {
        "<h1": '<h1 class="text-5xl mb-4 mt-6"',
        "<h2": '<h2 class="text-4xl mb-3 mt-5"',
        "<h3": '<h3 class="text-3xl mb-2 mt-4"',
        "<h4": '<h4 class="text-2xl mb-1 mt-3"',
        "<h5": '<h5 class="text-1xl mb-0.5 mt-2"',
        "<a": '<a class="underline text-blue-600 hover:text-blue-800 visited:text-purple-600"',  # noqa: E501
        "<ul": '<ul class="list-disc ml-6"',
        "<p>": '<p class="mb-2">',
    }
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], html)


def apply_custom_highlight_style(html: str) -> str:  # Would be better w/ re
    classes_to_highlight = ["highlight"]
    for class_name in classes_to_highlight:
        html = html.replace(
            f'class="{class_name}"',
            f'class="{class_name}" style="{HIGHLIGHT_STYLE}"',
        )
    return html


def markdown(text: str) -> ui.html:
    """Renders markdown text as a formatted html element.

    NOTE: The Mathjax script must have been added to the page already in order for math
    equations to render."""

    async def _render_math():
        await ui.run_javascript("MathJax.typeset()", respond=False)

    ui.add_body_html(MATHJAX_SCRIPTS)
    print("suppossedly added mathjax scripts")
    html = markdown_to_html_with_math(text)
    html = apply_tailwind(html)
    html = apply_custom_highlight_style(html)
    element = ui.html(html)
    ui.timer(0.1, _render_math, once=True)
    return element


if __name__ in {"__main__", "__mp_main__"}:
    mathjax_scripts = """
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
    """
    ui.add_body_html(mathjax_scripts)

    # Raw string is important for parser to not remove '\b', '\t', etc. from math
    example_md_text = r"""
This is inline code: `hello world`

This is block code:

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
np.linalg.det(A)
```

This is inline math: $\text{det}(A)$

This is block math:

$$ A = \begin{bmatrix} a & b \\ c & d \end{bmatrix} $$

This is a gif:

![silly cat](https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif)
"""

    markdown(example_md_text)
    ui.run()
