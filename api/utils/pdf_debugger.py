def debug_pdf_words(document, page_number=1):

    page = next(
        (p for p in document.pages if p.page_number == page_number),
        None
    )

    if page is None:
        return

    print(f"\n--- DEBUG PDF PAGE {page_number} ---")

    for word in page.words:
        print(
            f"{word.text:<25} "
            f"x0={word.x0:7.2f} "
            f"x1={word.x1:7.2f} "
            f"y0={word.y0:7.2f} "
            f"y1={word.y1:7.2f}"
        )