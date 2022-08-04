from interrogatio.validators import RequiredValidator

from connect.cli.plugins.project.utils import slugify
from connect.cli.plugins.project.validators import PythonIdentifierValidator

REPORT_BOOTSTRAP_WIZARD_INTRO = (
    'Welcome to the Connect Reports Project Bootstrap utility.\n'
    'Using this utility multiple data will be collected in order to create a project\n'
    'skeleton for your Connect Reports. This skeleton will contain all needed things\n'
    'to start writing your code.\n\n'
    'For more information please visit https://connect.cloudblue.com/community/sdk/connect-reports-sdk\n'
    'Have a nice trip!\n'
)

REPORT_ADD_WIZARD_INTRO = (
    'Welcome to the Add report to Reports project utility.\n'
    'Using this utility multiple data will be collected in order to add new report\n'
    'skeleton to your your Connect Reports project. This skeleton will contain all needed things\n'
    'to start writing your code.\n\n'
    'For more information please visit https://connect.cloudblue.com/community/sdk/connect-reports-sdk\n'
    'Have a nice trip!\n'
)


ADD_REPORT_QUESTIONS = [  # pragma: no cover
    {
        'name': 'initial_report_name',
        'label': 'Report: name',
        'type': 'input',
        'description': 'Enter the name of your new reports: ',
        'default': 'Another Awesome Report',
        'validators': (RequiredValidator(message='Please, provide a report name.'),),
    },
    {
        'name': 'initial_report_slug',
        'label': 'Report: module',
        'type': 'input',
        'description': 'Enter the module name of your new reports: ',
        'default': lambda x: slugify(x['initial_report_name']),
        'validators': (
            RequiredValidator(message='Please, provide a report module name.'),
            PythonIdentifierValidator(),
        ),
    },
    {
        'name': 'initial_report_description',
        'label': 'Report: description',
        'type': 'input',
        'description': 'Briefly describe your new report: ',
        'default': 'This report provides all data I need',
        'validators': (RequiredValidator(message='Please, provide a description.'),),
    },
    {
        'name': 'use_asyncio',
        'label': 'Report: asyncio',
        'type': 'selectone',
        'description': 'Do you want to develop your Report using the Python asyncio library?',
        'values': [
            ('n', 'No'),
            ('y', 'Yes'),
        ],
        'formatting_template': '${label}',
    },
    {
        'name': 'initial_report_renderer',
        'label': 'Report: default format',
        'type': 'selectone',
        'description': 'Select the default output format for your new report: ',
        'values': [
            ('xlsx', 'Microsoft Excel 2020 (XLSX)'),
            ('csv', 'Comma Separated Values (CSV)'),
            ('pdf', 'Portable Document Format (PDF)'),
            ('json', 'Javascript Object Notation (JSON)'),
            ('jinja2', 'Custom format using a Jinja2 template'),
        ],
        'formatting_template': '${label}',
    },
]


BOOTSTRAP_QUESTIONS = [  # pragma: no cover
    {
        'name': 'project_name',
        'label': 'Project: name',
        'type': 'input',
        'description': 'Enter a friendly name for your Reports project:',
        'default': 'My Awesome Project',
        'validators': (RequiredValidator(message='Please, provide a project name.'),),
    },
    {
        'name': 'project_slug',
        'label': 'Project: root',
        'type': 'input',
        'description': (
            'Choose a name for the root folder of your Reports module.'
            ' This must be a valid python\nidentifier:'
        ),
        'default': lambda x: slugify(x['project_name']),
        'validators': (
            RequiredValidator(message='Please, provide a project root folder.'),
            PythonIdentifierValidator(),
        ),
    },
    {
        'name': 'author',
        'label': 'Project: author',
        'type': 'input',
        'description': 'Please enter the author for this project:',
        'default': 'Globex Corporation',
        'validators': (RequiredValidator(message='Please, provide an author name.'),),
    },
    {
        'name': 'description',
        'label': 'Project: description',
        'type': 'input',
        'description': 'Briefly describe your Reports project:',
        'default': 'Project description',
        'validators': (RequiredValidator(message='Please, provide a description.'),),
    },
    {
        'name': 'package_name',
        'label': 'Project: package',
        'type': 'input',
        'description': (
            'Choose a name for the root python package of your Reports module.'
            ' This must be a valid python\nidentifier:'
        ),
        'default': 'reports',
        'validators': (
            RequiredValidator(message='Please, provide a package name.'),
            PythonIdentifierValidator(),
        ),
    },
    {
        'name': 'use_asyncio',
        'label': 'Project: asyncio',
        'type': 'selectone',
        'description': 'Do you want to develop your Report using the Python asyncio library?',
        'values': [
            ('n', 'No'),
            ('y', 'Yes'),
        ],
        'formatting_template': '${label}',
    },
    {
        'name': 'version',
        'label': 'Project: version',
        'type': 'input',
        'description': 'Introduce a version identifier for your Reports project:',
        'default': '0.1.0',
        'validators': (RequiredValidator(message='Please, provide a version.'),),
    },
    {
        'name': 'license',
        'label': 'Project: license',
        'type': 'selectone',
        'description': 'Choose an Open Source license for your Reports project:',
        'values': [
            ('Apache Software License 2.0', 'Apache Software License 2.0'),
            ('MIT', 'MIT'),
            ('BSD', 'BSD'),
        ],
        'formatting_template': '${label}',
    },
    {
        'name': 'use_github_actions',
        'label': 'Project: CI',
        'type': 'selectone',
        'description': (
            'If you plan to host the Reports code on GitHub, are you also planning\n'
            'to use GitHub actions as your continuous integration system ?'
        ),
        'values': [
            ('n', 'No'),
            ('y', 'Yes'),
        ],
        'formatting_template': '${label}',
    },
    {
        'name': 'initial_report_name',
        'label': 'Report: name',
        'type': 'input',
        'description': 'Enter the name of your initial reports: ',
        'default': 'My Awesome Report',
        'validators': (RequiredValidator(message='Please, provide a report name.'),),
    },
    {
        'name': 'initial_report_slug',
        'label': 'Report: module',
        'type': 'input',
        'description': 'Enter the module name of your initial reports: ',
        'default': lambda x: slugify(x['initial_report_name']),
        'validators': (
            RequiredValidator(message='Please, provide a report module name.'),
            PythonIdentifierValidator(),
        ),
    },
    {
        'name': 'initial_report_description',
        'label': 'Report: description',
        'type': 'input',
        'description': 'Briefly describe your initial report: ',
        'default': 'This report provides all data I need',
        'validators': (RequiredValidator(message='Please, provide a description.'),),
    },
    {
        'name': 'initial_report_renderer',
        'label': 'Report: default format',
        'type': 'selectone',
        'description': 'Select the default output format for your initial report: ',
        'values': [
            ('xlsx', 'Microsoft Excel 2020 (XLSX)'),
            ('csv', 'Comma Separated Values (CSV)'),
            ('pdf', 'Portable Document Format (PDF)'),
            ('json', 'Javascript Object Notation (JSON)'),
            ('jinja2', 'Custom format using a Jinja2 template'),
        ],
        'formatting_template': '${label}',
    },
]


REPORT_SUMMARY = """<b><blue>Report</blue></b>
    <b>Name:</b> ${initial_report_name}
    <b>Description:</b> ${initial_report_description}
    <b>Output format:</b> ${initial_report_renderer}
    <b>Use Asyncio:</b> ${use_asyncio}
"""

BOOTSTRAP_SUMMARY = """<b><blue>Project</blue></b>
    <b>Project Name:</b> ${project_name} - <b>Package Name:</b> ${package_name}
    <b>Description:</b> ${description}
    <b>Author:</b> ${author}
    <b>Version:</b> ${version} - <b>License:</b> ${license}
    <b>Use Github Actions:</b> ${use_github_actions}
""" + REPORT_SUMMARY
