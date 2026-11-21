"""Generate an Arabic poem with a local Ollama model."""

import re
from collections import Counter
from pathlib import Path

import ollama

from prompts import TEMPLATES, DEFAULT_METER, DEFAULT_QAFIYA

ARABIC_LETTER = re.compile(r"[\u0600-\u06FF]")
# Anything that is not Arabic, whitespace or common punctuation.
FOREIGN = re.compile(r"[^\u0600-\u06FF\s\u200c-\u200f.…,،؛:!؟\-()«»]")
DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")


def clean_poem(text, num_verses):
    """Return up to num_verses bayts, one per line, as 'half ... half'.

    The model sometimes writes each hemistich on its own line instead of
    putting both halves of a bayt on one line, so the layout is
    normalized here. Blank lines, quotes and English text are removed.
    """
    lines = []
    for line in text.splitlines():
        line = line.strip().strip('"').strip("'").strip()
        line = line.strip(".…").strip()
        if line and ARABIC_LETTER.search(line):
            lines.append(line)

    with_separator = [line for line in lines if "..." in line]
    if len(with_separator) * 2 >= len(lines):
        verses = lines                      # already one bayt per line
    else:                                   # one hemistich per line: pair them
        verses = [f"{lines[i]} ... {lines[i + 1]}"
                  for i in range(0, len(lines) - 1, 2)]
    return "\n".join(verses[:num_verses])


def normalize(word):
    """Remove diacritics and unify letter variants before comparing."""
    word = DIACRITICS.sub("", word)
    word = re.sub(r"[^\u0600-\u06FF]", "", word)
    for old, new in (("ى", "ي"), ("ة", "ه"), ("أ", "ا"),
                     ("إ", "ا"), ("آ", "ا")):
        word = word.replace(old, new)
    return word


def last_word(line):
    """Normalized last word of a line (after the '...' separator)."""
    words = line.split("...")[-1].split()
    return normalize(words[-1]) if words else ""


def last_letter(line):
    """Rhyme letter: last letter of the last word, ignoring stray letters."""
    word = last_word(line)
    return word[-1] if len(word) >= 3 else ""


def has_stray_endings(poem):
    """True if a line ends with a single letter or a very short fragment."""
    return any(len(last_word(line)) < 3 for line in poem.splitlines())


def rhyme_consistency(poem):
    """Share of lines whose last word ends with the most common letter.

    Lines ending in a stray letter count as failures. 1.00 means every
    line ends with a real-looking word with the same final letter. It is a
    simple approximation of qafiya, not a full prosodic analysis.
    """
    lines = poem.splitlines()
    if not lines:
        return 0.0
    letters = [last_letter(line) for line in lines]
    valid = [letter for letter in letters if letter]
    if not valid:
        return 0.0
    return Counter(valid).most_common(1)[0][1] / len(lines)


def has_foreign_characters(poem):
    """True if the poem contains letters from another script."""
    return bool(FOREIGN.search(poem))


def generate_poem(theme, style="classical", num_verses=4,
                  template="structured", model="llama3",
                  meter=DEFAULT_METER, qafiya=DEFAULT_QAFIYA,
                  tries=1, temperature=None, repeat_penalty=None):
    """Return a poem for the given settings.

    With tries > 1, several poems are generated and the best one is kept,
    ranked by: right number of bayts, no foreign characters, no stray
    endings, then rhyme consistency. temperature and repeat_penalty are only
    sent when given, so by default Ollama uses its own defaults.
    """
    num_verses = int(num_verses)
    prompt = TEMPLATES[template].format(
        theme=theme, style=style, num_verses=num_verses,
        meter=meter, qafiya=qafiya,
    )
    options = {}
    if temperature is not None:
        options["temperature"] = temperature
    if repeat_penalty is not None:
        options["repeat_penalty"] = repeat_penalty

    best, best_key = "", None
    for _ in range(max(1, int(tries))):
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options=options,
        )
        poem = clean_poem(response["message"]["content"], num_verses)
        count_ok = len(poem.splitlines()) == num_verses
        clean = not has_foreign_characters(poem)
        no_stray = not has_stray_endings(poem)
        score = rhyme_consistency(poem)
        key = (count_ok, clean, no_stray, score)
        if best_key is None or key > best_key:
            best, best_key = poem, key
        if count_ok and clean and no_stray and score == 1.0:
            break
    return best


if __name__ == "__main__":
    THEME = "الوطن"
    STYLE = "classical"
    VERSES = 4
    TRIES = 3

    results = Path(__file__).resolve().parents[2] / "07_EXTRA" / "results"
    results.mkdir(parents=True, exist_ok=True)

    with open(results / "result.txt", "w", encoding="utf-8") as f:
        f.write(f"Theme: {THEME} | Style: {STYLE} | Verses: {VERSES} | "
                f"Meter: {DEFAULT_METER} | Tries: {TRIES} | "
                f"Model: llama3 (Ollama default settings)\n\n")
        for name in TEMPLATES:
            print(f"Generating with template: {name} ...")
            poem = generate_poem(THEME, STYLE, VERSES, template=name,
                                 tries=TRIES)
            n_lines = len(poem.splitlines())
            score = rhyme_consistency(poem)
            f.write(f"=== {name} | lines {n_lines}/{VERSES} | "
                    f"rhyme consistency {score:.2f} | "
                    f"foreign: {has_foreign_characters(poem)} | "
                    f"stray endings: {has_stray_endings(poem)} ===\n"
                    f"{poem}\n\n")
            f.flush()

    print("Done: 07_EXTRA/results/result.txt")
