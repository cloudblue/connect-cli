# Copyright © 2021 CloudBlue. All rights reserved.

import os

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)

report_spec = '{{ cookiecutter.report_spec }}'

if report_spec == 'v1':
    os.rename(
        os.path.join(PROJECT_DIRECTORY, 'entry_function_v1.py'),
        os.path.join(PROJECT_DIRECTORY, 'entrypoint.py'),
    )
    os.remove(os.path.join(PROJECT_DIRECTORY, 'entry_function_v2.py'))

elif report_spec == 'v2':
    os.rename(
        os.path.join(PROJECT_DIRECTORY, 'entry_function_v2.py'),
        os.path.join(PROJECT_DIRECTORY, 'entrypoint.py'),
    )
    os.remove(os.path.join(PROJECT_DIRECTORY, 'entry_function_v1.py'))
    os.remove(os.path.join(PROJECT_DIRECTORY, 'template.xlsx'))
