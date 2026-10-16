def group_words_by_line(
    words: list,
    tolerance: float = 4.0,
) -> list[list]:

    sorted_words = sorted(
        words,
        key=lambda word: (word[1], word[0]),
    )

    lines = []

    for word in sorted_words:
        y0 = word[1]

        if (
            lines
            and abs(lines[-1]["y"] - y0) <= tolerance
        ):
            lines[-1]["words"].append(word)

            ys = [
                w[1]
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
            key=lambda word: word[0],
        )
        for line in lines
    ]