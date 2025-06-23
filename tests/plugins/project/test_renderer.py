#  Copyright © 2025 CloudBlue. All rights reserved.

import os
import tempfile

import pytest

from connect.cli.plugins.project.renderer import BoilerplateRenderer


@pytest.mark.parametrize('context', (True, [], 'hola'))
def test_render_invalid_parameter_context(context):
    with pytest.raises(TypeError) as exc:
        BoilerplateRenderer(
            context=context,
            template_folder=None,
            output_dir=None,
        )
    assert 'The parameter context is invalid, it must be a dict.' in str(exc.value)


@pytest.mark.parametrize('template_folder', (True, [], {}, 'NonExistingFolder'))
def test_render_invalid_parameter_template_folder(template_folder):
    with pytest.raises(TypeError) as exc:
        BoilerplateRenderer(
            context={},
            template_folder=template_folder,
            output_dir=None,
        )
    assert 'The parameter template_folder is invalid, it must be a valid path string.' in str(
        exc.value,
    )


@pytest.mark.parametrize('output_dir', (True, [], {}))
def test_render_invalid_parameter_output_dir(output_dir):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, 'template_folder'))
        with pytest.raises(TypeError) as exc:
            BoilerplateRenderer(
                context={},
                template_folder=os.path.join(tmpdir, 'template_folder'),
                output_dir=output_dir,
            )
        assert 'The parameter output_dir is invalid, it must be a valid path string.' in str(
            exc.value,
        )


@pytest.mark.parametrize('overwrite', ('Si', [], {}))
def test_render_invalid_parameter_overwrite(overwrite):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, 'template_folder'))
        with pytest.raises(TypeError) as exc:
            BoilerplateRenderer(
                context={},
                template_folder=os.path.join(tmpdir, 'template_folder'),
                output_dir='output_dir',
                overwrite=overwrite,
            )
        assert 'The parameter overwrite is invalid, it must be bool type.' in str(exc.value)


@pytest.mark.parametrize('ftype', ('pre', 'post'))
@pytest.mark.parametrize('value', ('Si', True, {'hey': 'you'}, ['a']))
def test_render_invalid_parameter_pre_post_render(ftype, value):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, 'template_folder'))
        with pytest.raises(TypeError) as exc:
            BoilerplateRenderer(
                context={},
                template_folder=os.path.join(tmpdir, 'template_folder'),
                output_dir='output_dir',
                overwrite=True,
                **{f'{ftype}_render': value},
            )
        assert f'The parameter {ftype}_render is invalid, it must be callable.' in str(exc.value)


@pytest.mark.parametrize('exclude', ('Si', True, {'hey': 'you'}))
def test_render_invalid_parameter_exclude(exclude):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, 'template_folder'))
        with pytest.raises(TypeError) as exc:
            BoilerplateRenderer(
                context={},
                template_folder=os.path.join(tmpdir, 'template_folder'),
                output_dir='output_dir',
                overwrite=True,
                exclude=exclude,
            )
        assert 'The parameter exclude is invalid, it must be a list.' in str(exc.value)


def test_renderer_functions_executed(mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, 'template_folder'))
        pre_mock = mocker.MagicMock()
        post_mock = mocker.MagicMock()
        renderer = BoilerplateRenderer(
            context={},
            template_folder=os.path.join(tmpdir, 'template_folder'),
            output_dir='output_dir',
            overwrite=False,
            pre_render=pre_mock,
            post_render=post_mock,
        )
        renderer.render()
        assert pre_mock.call_count == 1
        assert post_mock.call_count == 1
