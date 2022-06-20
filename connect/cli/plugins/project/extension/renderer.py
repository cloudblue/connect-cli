import os
from string import Template

from click import ClickException
from jinja2 import Environment, FileSystemLoader, select_autoescape

from connect.cli.core.terminal import console
from connect.cli.plugins.project.utils import purge_dir


class BoilerplateRenderer:
    def __init__(self, base_dir, context, overwrite):
        self.base_dir = base_dir
        self.context = context
        self.overwrite = overwrite
        self.env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'template')),
            extensions=['jinja2_time.TimeExtension'],
            keep_trailing_newline=True,
            autoescape=select_autoescape(),
        )

    def render(self):
        with console.status("[magenta]Generating extension project"):
            directories = self._create_directories()
            templates = self.env.list_templates()
            for template in templates:
                out_dir = template.rsplit('/', 2)[-2]
                self._render_template(template, directories[out_dir])
            console.print()
        return directories['project_dir']

    def _create_directories(self):
        project_dir = os.path.join(self.base_dir, self.context['project_slug'])
        if os.path.exists(project_dir):
            if not self.overwrite:
                raise ClickException(f'The destination directory {project_dir} already exists.')
            purge_dir(project_dir)
        package_dir = os.path.join(project_dir, self.context['package_name'])
        tests_dir = os.path.join(project_dir, 'tests')
        os.makedirs(package_dir)
        console.print(f'Directory {package_dir} created [bold green]\u2713[/bold green]')
        os.makedirs(tests_dir, exist_ok=True)
        console.print(f'Directory {tests_dir} created [bold green]\u2713[/bold green]')
        github_dir = None
        if self.context['use_github_actions'] == 'y':
            github_dir = os.path.join(project_dir, '.github', 'workflows')
            os.makedirs(github_dir, exist_ok=True)
            console.print(f'Directory {github_dir} created [bold green]\u2713[/bold green]')
        return {
            'project_dir': project_dir,
            'package_dir': package_dir,
            'tests_dir': tests_dir,
            'github_dir': github_dir,
        }

    def _render_template(self, template_name, output_dir):
        if not output_dir:
            return
        template = self.env.get_template(template_name)
        output_file_tpl = os.path.join(output_dir, template_name.rsplit('/')[-1][:-3])
        output_file = Template(output_file_tpl).safe_substitute(self.context)
        rendered = template.render(self.context)
        with open(output_file, 'w') as outstream:
            outstream.write(f'{rendered.rstrip()}\n')
        console.print(f'File {output_file} generated [bold green]\u2713[/bold green]')
