# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.
import os
import fnmatch
from string import Template
from pathlib import Path
import shutil
import tempfile

from jinja2 import Environment, FileSystemLoader, select_autoescape

from connect.cli.core.terminal import console
from connect.cli.plugins.project.utils import purge_dir


class BoilerplateRenderer:

    def __init__(
        self,
        context,
        template_folder,
        output_dir,
        overwrite=False,
        pre_render=None,
        post_render=None,
        exclude=None,
    ):
        self._validate_args(
            context,
            template_folder,
            output_dir,
            overwrite,
            pre_render,
            post_render,
            exclude,
        )
        self.context = context
        self.template_folder = template_folder
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.pre_render_function = pre_render
        self.post_render_function = post_render
        self.excluded_patterns = self._get_excluded_patterns(template_folder, exclude or [])
        self.env = Environment(
            loader=FileSystemLoader(
                searchpath=template_folder,
            ),
            extensions=['jinja2_time.TimeExtension'],
            keep_trailing_newline=True,
            autoescape=select_autoescape(),
        )

    @staticmethod
    def _get_excluded_patterns(template_dir, exclude):
        excludes = []
        for pattern in exclude:
            excludes.extend(
                [
                    str(p) for p in Path(os.path.join(template_dir, '${project_slug}')).glob(pattern)
                ],
            )
        return excludes

    @staticmethod
    def _validate_args(context, template_folder, output_dir, overwrite, pre_render, post_render, exclude):
        if not isinstance(context, dict):
            raise TypeError('The parameter context is invalid, it must be a dict.')
        if not isinstance(template_folder, str) or not os.path.exists(template_folder):
            raise TypeError('The parameter template_folder is invalid, it must be a valid path string.')
        if not isinstance(output_dir, str):
            raise TypeError('The parameter output_dir is invalid, it must be a valid path string.')
        if not isinstance(overwrite, bool):
            raise TypeError('The parameter overwrite is invalid, it must be bool type.')
        if pre_render and not callable(pre_render):
            raise TypeError('The parameter pre_render is invalid, it must be callable.')
        if post_render and not callable(post_render):
            raise TypeError('The parameter post_render is invalid, it must be callable.')
        if exclude and not isinstance(exclude, list):
            raise TypeError('The parameter exclude is invalid, it must be a list.')

    def _create_directories(self, output_dir):
        for element in Path(self.template_folder).rglob('*'):
            directory = os.path.join(output_dir, os.path.relpath(str(element), self.template_folder))
            directory = Template(directory).safe_substitute(self.context)
            if element.is_dir() and not fnmatch.filter(self.excluded_patterns, element):
                os.makedirs(directory, exist_ok=True)
                console.print(
                    f'Folder {directory.replace(output_dir, "")}'
                    ' created [bold green]\u2713[/bold green]',
                )

    def render(self):
        if self.overwrite:
            purge_dir(self.output_dir)
            console.print(f'Directory {self.output_dir} deleted.')

        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_directories(output_dir=tmpdir)
            if self.pre_render_function:
                self.pre_render_function(tmpdir, self.context)
                console.print('pre_render_function executed [bold green]\u2713[/bold green]')
            with console.status('[magenta]Generating files'):
                templates = self.env.list_templates()
                for template in templates:
                    self._render_template(template, tmpdir)
                if self.post_render_function:
                    self.post_render_function(tmpdir, self.context)
                    console.print('post_render_function executed [bold green]\u2713[/bold green]')
                for folder in os.listdir(tmpdir):
                    shutil.move(
                        os.path.join(
                            tmpdir,
                            folder,
                        ),
                        self.output_dir,
                    )
                console.print('moved generated tree to destination [bold green]\u2713[/bold green]')
                console.print()

    def _render_template(self, template_name, destination):
        evaluated_template_path = Template(
            str(template_name),
        ).safe_substitute(
            self.context,
        )

        if not fnmatch.filter(self.excluded_patterns, os.path.join(self.template_folder, template_name)):
            file_destination = os.path.join(
                destination,
                evaluated_template_path[:-3],
            )
            template = self.env.get_template(template_name)
            content = template.render(self.context)
            with open(file_destination, 'w') as outstream:
                outstream.write(f'{content.rstrip()}\n')
            console.print(
                f'File {file_destination.replace(destination, "")}'
                ' generated [bold green]\u2713[/bold green]',
            )
