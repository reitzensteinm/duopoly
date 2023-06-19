import jinja2

TAG_COLOR_MAPPING = {
    "default": {"background": "white", "border": "black", "text": "black"},
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
					{{ trace_item.text }}
				</div>
			{% endfor %}
		</body>
		</html>
	"""
    )
    return template.render(trace_items=trace.items, tag_color_mapping=TAG_COLOR_MAPPING)
