import jinja2


def load_prompt(prompt_name):
    template_loader = jinja2.FileSystemLoader(searchpath="./prompts/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(prompt_name + ".txt")
    return template.render()
