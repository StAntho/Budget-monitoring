from io import StringIO
import markdown
import pandas as pd


def markdown_table_to_df(table_content: str) -> pd.DataFrame:
    html = markdown.markdown(
        table_content,
        extensions=["tables"],
    )

    tables = pd.read_html(
        StringIO(html),
        flavor="lxml",
    )

    if not tables:
        return pd.DataFrame()

    return tables[0]