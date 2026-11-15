
# ============================================
# Project 9: Arabic Poem / Story Generation
# File: prompts.py
# Task 1: Design 3 Prompt Templates
# ============================================


# Template 1: Poem Generation
def poem_prompt(theme, style, length):

    prompt = f"""
اكتب قصيدة باللغة العربية عن الموضوع التالي: {theme}

الأسلوب: {style}
عدد الأبيات: {length}

التعليمات:
- استخدم اللغة العربية الفصحى.
- اجعل القصيدة جميلة ومترابطة.
- التزم بالموضوع والأسلوب المطلوبين.
- حاول احترام القافية والإيقاع الشعري.
- لا تضف مقدمة أو ترجمة أو شرحا.
- اكتب القصيدة فقط.
"""
    return prompt


# Template 2: Classical Arabic Poem
def classical_poem_prompt(theme, length):

    prompt = f"""
اكتب قصيدة عربية فصحى بأسلوب كلاسيكي عن: {theme}

عدد الأبيات: {length}

التعليمات:
- استخدم مفردات عربية فصيحة.
- حاول الالتزام بقافية موحدة.
- اجعل الأبيات مترابطة في المعنى.
- استخدم تعابير أدبية جميلة.
- لا تضف أي شرح خارج القصيدة.
"""
    return prompt


# Template 3: Modern Arabic Story
def story_prompt(theme, style, length):

    prompt = f"""
اكتب قصة قصيرة باللغة العربية عن: {theme}

الأسلوب: {style}
الطول: {length}

التعليمات:
- ابدأ بمقدمة واضحة.
- اجعل الأحداث مترابطة ومنطقية.
- استخدم لغة عربية واضحة وسليمة.
- اختم القصة بنهاية مناسبة.
- لا تضف ترجمة أو شرحا.
اكتب القصة فقط.
"""
    return prompt
