from setuptools import find_packages, setup


def read_file(name):
    with open(name, 'r') as f:
        content = f.read().rstrip('\n')
    return content


setup(
    name='connect-cli',
    author='CloudBlue',
    url='https://connect.cloudblue.com',
    description='CloudBlue Connect Product Synchronizer CLI',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    zip_safe=True,
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_file('requirements/dev.txt').splitlines(),
    setup_requires=['setuptools_scm', 'pytest-runner', 'wheel'],
    use_scm_version=True,
    entry_points={
        'console_scripts': [
            'ccli = cnctcli.ccli:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
    ],
    keywords='fulfillment command line interface utility cli vendor connect cloudblue',

)
