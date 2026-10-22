from extraction.pdf_extractor import ExtractedWord

def group_words_by_line(
    words: list,
    tolerance: float = 4.0,
) -> list[list[ExtractedWord]]:
    sorted_words = sorted(
        words,
        key=lambda word: (word.y0, word.x0),
    )

    lines = []

    for word in sorted_words:
        y0 = word.y0

        if (
            lines
            and abs(lines[-1]["y"] - y0) <= tolerance
        ):
            lines[-1]["words"].append(word)

            ys = [
                w.y0
                for w in lines[-1]["words"]
            ]

            lines[-1]["y"] = sum(ys) / len(ys)

        else:
            lines.append({
                "y": y0,
                "words": [word],
            })

    return [
        sorted(
            line["words"],
            key=lambda word: word.x0,
        )
        for line in lines
    ]



def get_zone_text(
    words:  list[ExtractedWord],
    x_range: tuple[float, float],
) -> str:

    x_min, x_max = x_range

    selected = [
        word
        for word in words
        if word.x0 >= x_min and word.x1 <= x_max
    ]

    selected.sort(key=lambda word: word.x0)

    return " ".join(
        word.text
        for word in selected
    ).strip()
