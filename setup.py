from setuptools import find_packages, setup


def read_file(name):
    with open(name, 'r') as f:
        content = f.read().rstrip('\n')
    return content


setup(
    name='product-sync',
    author='CloudBlue',
    url='https://connect.cloudblue.com',
    description='CloudBlue Connect Product Synchronizer CLI',
    long_description=read_file('README.md'),
    python_requires='>=3.6',
    zip_safe=True,
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_file('requirements/dev.txt').splitlines(),
    setup_requires=['setuptools_scm', 'pytest-runner'],
    use_scm_version=True,
    entry_points={
        'console_scripts': [
            'ccli = cnctcli.ccli:main',
        ]
    },
)
