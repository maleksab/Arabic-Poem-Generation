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
    """Keep the first num_verses lines that contain Arabic letters.

    The model often ignores the requested length, adds blank lines or
    English text, and leaves a dangling '...', so this is fixed here.
    """
    lines = []
    for line in text.splitlines():
        line = line.strip().strip('"').strip("'").strip()
        line = line.strip(".…").strip()
        if line and ARABIC_LETTER.search(line):
            lines.append(line)
    return "\n".join(lines[:num_verses])


def normalize(word):
    """Remove diacritics and unify letter variants before comparing."""
    word = DIACRITICS.sub("", word)
    word = re.sub(r"[^\u0600-\u06FF]", "", word)
    for old, new in (("ى", "ي"), ("ة", "ه"), ("أ", "ا"),
                     ("إ", "ا"), ("آ", "ا")):
        word = word.replace(old, new)
    return word


def last_letter(line):
    """Last letter of the last word of a line (rhyme letter)."""
    words = line.split("...")[-1].split()
    if not words:
        return ""
    word = normalize(words[-1])
    return word[-1] if word else ""


def rhyme_consistency(poem):
    """Share of lines whose last word ends with the most common letter.

    1.00 means all lines end with the same letter. It is a simple
    approximation of rhyme (qafiya), not a full prosodic analysis.
    """
    letters = [last_letter(line) for line in poem.splitlines()]
    letters = [letter for letter in letters if letter]
    if not letters:
        return 0.0
    return Counter(letters).most_common(1)[0][1] / len(letters)


def has_foreign_characters(poem):
    """True if the poem contains letters from another script."""
    return bool(FOREIGN.search(poem))


def generate_poem(theme, style="classical", num_verses=4,
                  template="structured", model="llama3",
                  meter=DEFAULT_METER, qafiya=DEFAULT_QAFIYA,
                  tries=1, temperature=None, repeat_penalty=None):
    """Return a poem for the given settings.

    With tries > 1, several poems are generated and the one with the best
    rhyme consistency is kept; poems with foreign characters are skipped.
    temperature and repeat_penalty are only sent when given, so by default
    Ollama uses its own defaults (like `ollama run` in the terminal).
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

    best, best_score, last = "", -1.0, ""
    for _ in range(max(1, int(tries))):
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options=options,
        )
        poem = clean_poem(response["message"]["content"], num_verses)
        last = poem
        if has_foreign_characters(poem):
            continue
        score = rhyme_consistency(poem)
        if score > best_score:
            best, best_score = poem, score
        if score == 1.0:
            break
    return best or last

if __name__ == "__main__":
    THEME = "الوطن"
    STYLE = "classical"
    VERSES = 4
    TEMPLATE = "structured"
    TEMPERATURES = [0.3, 0.7, 1.0]
    RUNS = 2   # poems per temperature

    results = Path(__file__).resolve().parents[2] / "07_EXTRA" / "results"
    results.mkdir(parents=True, exist_ok=True)

    with open(results / "temperature_test.txt", "w", encoding="utf-8") as f:
        f.write(f"Theme: {THEME} | Style: {STYLE} | Verses: {VERSES} | "
                f"Template: {TEMPLATE} | Model: llama3\n\n")
        for temp in TEMPERATURES:
            for run in range(1, RUNS + 1):
                print(f"temperature {temp}, run {run} ...")
                poem = generate_poem(THEME, STYLE, VERSES,
                                     template=TEMPLATE, temperature=temp)
                n_lines = len(poem.splitlines())
                score = rhyme_consistency(poem)
                f.write(f"=== temperature {temp} | run {run} | "
                        f"lines {n_lines}/{VERSES} | "
                        f"rhyme consistency {score:.2f} ===\n{poem}\n\n")
                f.flush()

    print("Done: 07_EXTRA/results/temperature_test.txt")