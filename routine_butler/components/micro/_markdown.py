import re
from typing import List

import bs4
from bs4 import BeautifulSoup
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
            "toc",
            "tables",
            "pymdownx.tasklist",
            "pymdownx.superfences",
            "pymdownx.highlight",
            "pymdownx.arithmatex",
            "pymdownx.inlinehilite",
        ],
        extension_configs={
            "pymdownx.superfences": {
                "preserve_tabs": True,
            },
            "pymdownx.inlinehilite": {
                "style_plain_text": True,
            },
            "pymdownx.highlight": {
                "guess_lang": False,
                "noclasses": True,
                "linenums_style": "inline",
                "line_spans": "__codeline",
            },
            "pymdownx.arithmatex": {
                "smart_dollar": False,
                "preview": True,
                "generic": True,
            },
        },
    )
    html = md_parser.convert(markdown_text)
    return html


def apply_styles(
    element: bs4.element.Tag, styles: str, should_recurse: bool = False
):
    if should_recurse:
        for child in element.children:
            if isinstance(child, bs4.element.Tag):
                apply_styles(child, styles, should_recurse=True)

    old_styles = element.get("style")
    if old_styles:
        old_styles_dict = {}
        for style in old_styles.split(";"):
            if style:
                attribute = style.split(":")[0].strip()
                value = style.split(":")[1].strip()
                old_styles_dict[attribute] = value
        new_styles_dict = {}
        for style in styles.split(";"):
            if style:
                attribute = style.split(":")[0].strip()
                value = style.split(":")[1].strip()
                new_styles_dict[attribute] = value
        updated_styles_dict = {**old_styles_dict, **new_styles_dict}
        updated_styles = "; ".join(
            [f"{k}: {v}" for k, v in updated_styles_dict.items()]
        )
    else:
        updated_styles = styles
    element["style"] = updated_styles


def add_linebreaks_in_between_codelines(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Iterate through elements whose id name contains "__codeline"
    for element in soup.find_all(id=lambda x: x and "__codeline" in x):
        # Add a <br> tag thereafter
        element.insert_after(soup.new_tag("br"))
    return str(soup)


def apply_custom_table_style(html: str) -> str:
    table_styles = "border: 1px solid lightgray; padding: 4px;"
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        apply_styles(table, table_styles, should_recurse=True)
    return str(soup)


def apply_custom_highlight_style(html: str) -> str:  # Would be better w/ re?
    """A hacky way to replace old styles with new styles and achieve our custom
    highlighting style."""
    classes_to_highlight = ["highlight"]
    for class_name in classes_to_highlight:
        html = html.replace(
            f'class="{class_name}"',
            f'class="{class_name}" style="{HIGHLIGHT_STYLE}"',
        )
    return html


def apply_all_custom_style_modifications(html: str) -> str:
    html = apply_custom_highlight_style(html)
    html = apply_custom_table_style(html)
    html = add_linebreaks_in_between_codelines(html)
    replacements = {
        "<h1": '<h1 style="font-size: 40px; line-height: 44px; margin: 8px 0px 8px 0px"',  # noqa: E501
        "<h2": '<h1 style="font-size: 30px; line-height: 34px; margin: 8px 0px 8px 0px"',  # noqa: E501
        "<h3": '<h1 style="font-size: 25px; line-height: 29px; margin: 8px 0px 8px 0px"',  # noqa: E501
        "<h4": '<h1 style="font-size: 20px; line-height: 24px; margin: 8px 0px 8px 0px"',  # noqa: E501
        "<h5": '<h1 style="font-size: 17px; line-height: 21px; margin: 8px 0px 8px 0px"',  # noqa: E501
        "<a": '<a class="underline text-blue-600 hover:text-blue-800 visited:text-purple-600"',  # noqa: E501
        "<ul": '<ul class="list-disc ml-6"',  # Adds markers to unordered lists
        "<ol": '<ol class="list-decimal ml-6"',  # Add nums to ordered lists
        "<p": '<p class="my-2"',
    }
    pattern = re.compile("|".join(replacements.keys()))
    return pattern.sub(lambda m: replacements[re.escape(m.group(0))], html)


def preprocess_markdown(text: str) -> str:
    """Preprocesses markdown text to make it more suitable for rendering as html."""
    # Make sure that indented lines are indented with tabs
    text = text.replace("\n  ", "\n\t")
    # Make sure that all lists have a newline before them
    lines: List[str] = text.split("\n")
    updated_lines = []
    for i, line in enumerate(text.split("\n")):
        if i == 0:
            updated_lines.append(line)
            continue  # Skip first line
        stripped_prev_line = lines[i - 1].strip()
        stripped_cur_line = line.strip()
        if (
            stripped_prev_line
            and stripped_cur_line
            and stripped_prev_line[0].isalpha()
            and (
                stripped_cur_line[0] in {"-", "*", "+"}
                or stripped_cur_line[0].isdigit()
            )
        ):
            updated_lines.append("")  # Add newline before list
            updated_lines.append(line)
        else:
            updated_lines.append(line)
    text = "\n".join(updated_lines)
    return text


def markdown(text: str) -> ui.html:
    """Renders markdown text as a formatted html element.

    NOTE: The Mathjax script must have been added to the page already in order for math
    equations to render."""

    async def _render_math():
        await ui.run_javascript("MathJax.typeset()", respond=False)

    ui.add_body_html(MATHJAX_SCRIPTS)
    text = preprocess_markdown(text)
    html = markdown_to_html_with_math(text)
    element = ui.html(apply_all_custom_style_modifications(html))
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
This is a table of contents:

- [Title](#title)
    * [Subtitle 1](#subtitle-1)
        + [Subtitle 2](#subtitle-2)
        - [Subtitle 3](#subtitle-3)
            * [Subtitle 4](#subtitle-4)

# Title

## Subtitle 1

### Subtitle 2

#### Subtitle 3

##### Subtitle 4

This is inline code: `hello world`

This is block code:

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
np.linalg.det(A)
```

This is a list:
- item 1.0
- item 2.0

This is _another_ list:

- item 1.0
- item 2.0

This is a **_numbered_** list:

1. item 1.0

2. item 2.0


This is a **nested** list:

- item 1.0
- item 2.0
  - item 2.1
  - item 2.2

This is a task list:

-   [X] item 1
    *   [X] item A
    *   [ ] item B
        more text
        +   [x] item a
        +   [ ] item b
        +   [x] item c
    *   [X] item C
-   [ ] item 2
-   [ ] item 3

This is a markdown table:

| Item              | In Stock | Price |
| ---------------- | ------ | ---- |
| Python Hat        |   True   | 23.99 |


This is inline math: $\text{det}(A)$

This is block math:

$$ A = \begin{bmatrix} a & b \\ c & d \end{bmatrix} $$

This is a raw html table:

<table>
<tbody>
<tr>
<td style="background-color:rgba(255, 0, 0, 0.3);">📚</td>
</tr>
<tr>
<td style="background-color:rgba(255, 0, 0, 0.3);">📚</td>
</tr>
<tr>
<td style="background-color:rgba(0, 255, 0, 0.3);">📚</td>
</tr>
<tr>
<td style="background-color:rgba(0, 255, 0, 0.3);">📚</td>
</tr>
<tr>
<td style="background-color:rgba(0, 255, 0, 0.3);">📚</td>
</tr>
</tbody>
</table>

This is a gif:

![silly cat](https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif)
"""

    markdown(example_md_text)
    ui.run()
