from extraction.pdf_extractor import ExtractedDocument

class MarkdownExporter:

    @staticmethod
    def _cell(value) -> str:
        return (
            str(value or "")
            .strip()
            .replace("|", r"\|")
            .replace("\n", "<br>")
        )

    def export(
        self,
        document: ExtractedDocument,
    ) -> str:
        page_blocks = []

        for page in document.pages:
            table_items = []

            for table in page.tables:
                rows = table.rows

                if not rows:
                    continue

                headers = [
                    self._cell(value)
                    for value in rows[0]
                ]

                lines = [
                    "| " + " | ".join(headers) + " |",
                    "| " + " | ".join(
                        "---" for _ in headers
                    ) + " |",
                ]

                for row in rows[1:]:
                    lines.append(
                        "| "
                        + " | ".join(
                            self._cell(value)
                            for value in row
                        )
                        + " |"
                    )

                table_items.append(
                    (
                        table.bbox[1],
                        "\n".join(lines),
                    )
                )

            table_items.sort(
                key=lambda item: item[0]
            )

            blocks = [
                content
                for _, content in table_items
            ]

            page_blocks.append(
                "\n\n".join(blocks)
            )

        full_markdown = (
            "\n\n<!-- page break -->\n\n"
        ).join(page_blocks)

        start_page = 1
        end_page = len(document.pages)

        return (
            f"<!-- pdf pages {start_page}-{end_page} -->\n\n"
            f"{full_markdown}"
        )