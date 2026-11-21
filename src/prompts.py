"""Prompt templates for Arabic poem generation (Project 9 MVP).

Three prompting strategies are compared:
  minimal    - zero-shot baseline (theme, style, length)
  structured - explicit meter and rhyme rules, no example
  fewshot    - three classical Arabic examples, no meter/rhyme rules

Structure inspired by a draft suggested by ChatGPT, then adapted
(Arabic examples, strict verse definition, no-repetition rule).
"""

# One verse = one line made of two hemistichs separated by " ... ".
VERSE_RULE = (
    "Write exactly {num_verses} lines. Each line is one verse (bayt) made of "
    "two hemistichs separated by \" ... \". Do not write blank lines, "
    "do not group lines into stanzas, and do not write more or fewer lines."
)

# Shared by all three templates so that the comparison stays fair.
NO_REPEAT_RULE = (
    "Do not repeat words: every verse must use different words and "
    "different ideas, no word (except small function words such as "
    "في، من، و) may appear twice in the poem, and no two lines may end "
    "with the same word."
)

OUTPUT_RULE = (
    "Write only the poem in Arabic. Do not translate it and do not add "
    "any explanation."
)

# Template A: minimal / zero-shot (baseline)
TEMPLATE_MINIMAL = (
    "Write an Arabic poem about {theme}.\n"
    "Style: {style}.\n"
    + VERSE_RULE + "\n"
    + NO_REPEAT_RULE + "\n"
    + OUTPUT_RULE
)

# Template B: structured, with meter and rhyme rules (no example)
TEMPLATE_STRUCTURED = (
    "You are a skilled Arabic poet. Write a poem in Modern Standard Arabic "
    "about the following theme: {theme}.\n"
    "Style: {style}.\n"
    + VERSE_RULE + "\n"
    + NO_REPEAT_RULE + "\n"
    "Meter (bahr): {meter}. Keep the same rhythm in every line.\n"
    "Rhyme (qafiya): {qafiya}.\n"
    "Requirements:\n"
    "- Follow the specified meter and rhyme.\n"
    "- Use only real Arabic words and Arabic letters.\n"
    "- " + OUTPUT_RULE + "\n"
    "- Start the poem directly.\n\n"
    "Poem:"
)

# Template C: few-shot with three classical Arabic examples
TEMPLATE_FEWSHOT = (
    "You are an Arabic poet. Write poems in the style of classical Arabic "
    "poetry, always in Arabic.\n\n"
    "Example 1:\n"
    "Theme: الصبر\n"
    "Style: classical\n"
    "Number of verses: 2\n"
    "Poem:\n"
    "دع الأيام تفعل ما تشاء ... وطب نفسا إذا حكم القضاء\n"
    "ولا تجزع لحادثة الليالي ... فما لحوادث الدنيا بقاء\n\n"
    "Example 2:\n"
    "Theme: العزيمة\n"
    "Style: classical\n"
    "Number of verses: 2\n"
    "Poem:\n"
    "على قدر أهل العزم تأتي العزائم ... وتأتي على قدر الكرام المكارم\n"
    "وتعظم في عين الصغير صغارها ... وتصغر في عين العظيم العظائم\n\n"
    "Example 3:\n"
    "Theme: الفخر\n"
    "Style: classical\n"
    "Number of verses: 2\n"
    "Poem:\n"
    "الخيل والليل والبيداء تعرفني ... والسيف والرمح والقرطاس والقلم\n"
    "صحبت في الفلوات الوحش منفردا ... حتى تعجب مني القور والأكم\n\n"
    "Now write a NEW and different poem (do not copy the examples):\n"
    "Theme: {theme}\n"
    "Style: {style}\n"
    + VERSE_RULE + "\n"
    + NO_REPEAT_RULE + "\n"
    + OUTPUT_RULE + "\n"
    "Poem:"
)

TEMPLATES = {
    "minimal": TEMPLATE_MINIMAL,
    "structured": TEMPLATE_STRUCTURED,
    "fewshot": TEMPLATE_FEWSHOT,
}

# Default values for the app and the scripts
DEFAULT_METER = "Al-Tawil"
DEFAULT_QAFIYA = (
    "choose ONE rhyme ending of one or two letters, and make the last "
    "word of the second hemistich of every bayt a complete, real Arabic "
    "word that ends with that same ending. Never write the ending as a "
    "separate word and never cut a word to make it fit"
)
DEFAULT_METERS = ["Al-Tawil", "Al-Basit", "Al-Kamil", "Al-Wafir",
                  "Al-Ramal", "Al-Khafif"]
DEFAULT_STYLES = ["classical", "modern", "dialectal"]
DEFAULT_THEMES = ["الحب", "الوطن", "الأم", "الغربة", "الطبيعة",
                  "الصداقة", "الأمل"]
