"""Generate an Arabic poem with a local Ollama model.

The poem is the model's raw answer: it is NOT cleaned, cut or retried.
The functions below only MEASURE the output (line count, rhyme, foreign
characters); they never change it.
"""

import re
from collections import Counter
from pathlib import Path

import ollama

from prompts import TEMPLATES, DEFAULT_METER, DEFAULT_QAFIYA

# Anything that is not Arabic, whitespace or common punctuation.
FOREIGN = re.compile(r"[^\u0600-\u06FF\s\u200c-\u200f.…,،؛:!؟\-()«»]")
DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")


def poem_lines(text):
    """Non-empty lines of the raw answer (used only for measuring)."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def normalize(word):
    """Remove diacritics and unify letter variants before comparing."""
    word = DIACRITICS.sub("", word)
    word = re.sub(r"[^\u0600-\u06FF]", "", word)
    for old, new in (("ى", "ي"), ("ة", "ه"), ("أ", "ا"),
                     ("إ", "ا"), ("آ", "ا")):
        word = word.replace(old, new)
    return word


def last_word(line):
    """Normalized last word of a line (after the '...' separator, if any)."""
    words = line.split("...")[-1].split()
    return normalize(words[-1]) if words else ""


def last_letter(line):
    """Rhyme letter: last letter of the last word, ignoring stray letters."""
    word = last_word(line)
    return word[-1] if len(word) >= 3 else ""


def count_lines(poem):
    """Number of non-empty lines in the raw answer."""
    return len(poem_lines(poem))


def count_separators(poem):
    """Number of lines that contain the ' ... ' hemistich separator."""
    return len([line for line in poem_lines(poem) if "..." in line])


def has_stray_endings(poem):
    """True if a line ends with a single letter or a very short fragment."""
    return any(len(last_word(line)) < 3 for line in poem_lines(poem))


def rhyme_consistency(poem):
    """Share of lines whose last word ends with the most common letter.

    1.00 means every line ends with a word with the same final letter. It
    is a simple approximation of qafiya, not a full prosodic analysis.
    """
    lines = poem_lines(poem)
    if not lines:
        return 0.0
    letters = [last_letter(line) for line in lines]
    valid = [letter for letter in letters if letter]
    if not valid:
        return 0.0
    return Counter(valid).most_common(1)[0][1] / len(lines)


def has_foreign_characters(poem):
    """True if the answer contains letters from another script."""
    return bool(FOREIGN.search(poem))


def generate_poem(theme, style="classical", num_verses=4,
                  template="structured", model="llama3",
                  meter=DEFAULT_METER, qafiya=DEFAULT_QAFIYA,
                  temperature=None, repeat_penalty=None, seed=None):
    """Return the model's raw answer for the given settings.

    Nothing is cleaned or retried. temperature, repeat_penalty and seed are
    only sent when given, so by default Ollama uses its own defaults.
    """
    prompt = TEMPLATES[template].format(
        theme=theme, style=style, num_verses=int(num_verses),
        meter=meter, qafiya=qafiya,
    )
    options = {}
    if temperature is not None:
        options["temperature"] = temperature
    if repeat_penalty is not None:
        options["repeat_penalty"] = repeat_penalty
    if seed is not None:
        options["seed"] = seed

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options=options,
    )
    return response["message"]["content"]


if __name__ == "__main__":
    from datetime import datetime

    THEMES = ["الصداقة"]      # one theme, or several: ["الأم", "الحب"]
    STYLE = "classical"
    VERSES = 4

    results = Path(__file__).resolve().parents[2] / "07_EXTRA" / "results"
    results.mkdir(parents=True, exist_ok=True)

    with open(results / "result.txt", "a", encoding="utf-8") as f:
        f.write(f"##### Run {datetime.now():%Y-%m-%d %H:%M} | Style: {STYLE} "
                f"| Verses: {VERSES} | Model: llama3 | RAW output "
                f"(Ollama default settings)\n\n")
        for theme in THEMES:
            for name in TEMPLATES:
                print(f"Generating: {theme} | {name} ...")
                poem = generate_poem(theme, STYLE, VERSES, template=name)
                f.write(f"=== {theme} | {name} | "
                        f"non-empty lines {count_lines(poem)} "
                        f"(requested {VERSES} verses) | "
                        f"lines with '...' {count_separators(poem)} | "
                        f"rhyme consistency {rhyme_consistency(poem):.2f} | "
                        f"foreign: {has_foreign_characters(poem)} | "
                        f"stray endings: {has_stray_endings(poem)} ===\n"
                        f"{poem}\n\n")
                f.flush()

    print("Done: 07_EXTRA/results/result.txt")