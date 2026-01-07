import markdown


def ai_answer_to_qt_html(text: str) -> str:
    html_body = markdown.markdown(
        text,
        extensions=[
            "fenced_code",
            "tables",
            "codehilite",
            "pymdownx.arithmatex",
        ],
        extension_configs={
            "pymdownx.arithmatex": {
                "generic": True
            }
        }
    )

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
body {{
    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
}}

h1, h2, h3 {{
    margin-top: 1em;
}}

pre {{
    background: #1e1e1e;
    color: #eaeaea;
    padding: 10px;
    border-radius: 6px;
    overflow-x: auto;
}}

code {{
    color: #ffd479;
}}

table {{
    border-collapse: collapse;
}}

th, td {{
    border: 1px solid #aaa;
    padding: 6px 10px;
}}

blockquote {{
    border-left: 4px solid #aaa;
    padding-left: 10px;
    color: #555;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""
