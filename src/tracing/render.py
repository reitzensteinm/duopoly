import jinja2

TAG_COLOR_MAPPING = {
    "default": {"background": "white", "border": "black", "text": "black"},
    "gpt-input": {"background": "#000000", "border": "#808080", "text": "#2DE864"},
    "gpt-output": {"background": "#000000", "border": "#808080", "text": "#A3E8FA"},
    "exception": {"background": "#000000", "border": "#FF0000", "text": "#FF9698"},
    # Add tag to color mapping here
    # Format: 'tag': {'background': 'color', 'border': 'color', 'text': 'color'}
}


def render_trace(trace) -> str:
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader("./templates/tracing/")
    ).get_template("trace.html")
    return template.render(
        trace_items=trace.trace_data, tag_color_mapping=TAG_COLOR_MAPPING
    )
