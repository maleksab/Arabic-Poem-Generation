"""Gradio interface for Arabic poem generation (Project 9)."""

import gradio as gr

from generate_poem import generate_poem
from prompts import DEFAULT_METERS, DEFAULT_QAFIYA, DEFAULT_STYLES, TEMPLATES


def _poem(theme, style, num_verses, template, meter, qafiya):
    """Generate one poem; return an error message if Ollama fails."""
    try:
        return generate_poem(
            theme.strip(),
            style,
            int(num_verses),
            template=template,
            meter=meter,
            qafiya=(qafiya or "").strip() or DEFAULT_QAFIYA,
        )
    except Exception as error:
        return (f"Error: {error}\n"
                "Check that Ollama is running and that llama3 is installed.")


def run_one(theme, style, num_verses, template, meter, qafiya):
    """Generate with the selected template and describe what was used."""
    if not theme or not theme.strip():
        return "Please enter a theme.", ""
    poem = _poem(theme, style, num_verses, template, meter, qafiya)
    lines = len([line for line in poem.splitlines() if line.strip()])
    info = (f"Template: {template} | Style: {style} | "
            f"Lines: {lines}/{int(num_verses)}")
    return poem, info


def run_all(theme, style, num_verses, meter, qafiya):
    """Generate one poem per template with the same settings."""
    if not theme or not theme.strip():
        return ["Please enter a theme."] * len(TEMPLATES)
    return [_poem(theme, style, num_verses, name, meter, qafiya)
            for name in TEMPLATES]


with gr.Blocks(title="Arabic Poem Generator") as demo:
    gr.Markdown(
        "# Arabic Poem Generator\n"
        "Llama 3 running locally through Ollama. One poem takes a minute "
        "or two; comparing all templates takes about three times longer. "
        "Meter and rhyme are only used by the *structured* template."
    )

    theme = gr.Textbox(label="Theme", placeholder="مثال: الوطن")
    style = gr.Radio(DEFAULT_STYLES, value="classical", label="Style")
    verses = gr.Slider(2, 12, value=4, step=1, label="Number of verses")
    meter = gr.Dropdown(DEFAULT_METERS, value=DEFAULT_METERS[0],
                        label="Meter (structured template)")
    qafiya = gr.Textbox(value=DEFAULT_QAFIYA,
                        label="Rhyme / qafiya (structured template)")

    gr.Markdown("### One template")
    template = gr.Dropdown(list(TEMPLATES), value="structured",
                           label="Prompt template")
    one_button = gr.Button("Generate one poem", variant="primary")
    one_output = gr.Textbox(label="Poem", lines=12, rtl=True)
    one_info = gr.Textbox(label="Settings used", interactive=False)
    one_button.click(run_one,
                     [theme, style, verses, template, meter, qafiya],
                     [one_output, one_info])

    gr.Markdown("### Compare all templates (same settings)")
    all_button = gr.Button("Generate with all templates")
    with gr.Row():
        all_outputs = [gr.Textbox(label=name, lines=12, rtl=True)
                       for name in TEMPLATES]
    all_button.click(run_all,
                     [theme, style, verses, meter, qafiya],
                     all_outputs)

if __name__ == "__main__":
    demo.launch()