import jinja2

TAG_COLOR_MAPPING = {
    "default": {"background": "white", "border": "black", "text": "black"},
    "gpt-input": {"background": "#000000", "border": "#808080", "text": "#00008B"},
    "gpt-output": {"background": "#000000", "border": "#808080", "text": "#ADD8E6"},
    "exception": {"background": "#000000", "border": "#FF0000", "text": "#FF0000"},
    # Add tag to color mapping here
    # Format: 'tag': {'background': 'color', 'border': 'color', 'text': 'color'}
}


def render_trace(trace) -> str:
    template = jinja2.Template(
        """
		<html>
		<head>
			<style>
				.panel {
					padding: 10px;
					border: 8px solid black;
					margin: 16px;
				}
				{% for tag, colors in tag_color_mapping.items() %}
				.bg-{{ tag }} {
					background-color: {{ colors['background'] }};
					border-color: {{ colors['border'] }};
					color: {{ colors['text'] }};
				}
				{% endfor %}
			</style>
		</head>
		<body>
			{% for trace_item in trace_items %}
				<div class="panel bg-{{ trace_item.tag }}">
					<pre>{{ trace_item.trace }}</pre>
				</div>
			{% endfor %}
		</body>
		</html>
		"""
    )
    return template.render(
        trace_items=trace.trace_data, tag_color_mapping=TAG_COLOR_MAPPING
    )
