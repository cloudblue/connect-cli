from setuptools import find_packages, setup


def read_file(name):
    with open(name, 'r') as f:
        content = f.read().rstrip('\n')
    return content


setup(
    name='ccli',
    author='CloudBlue',
    url='https://connect.cloudblue.com',
    description='CloudBlue Connect CLI',
    long_description=read_file('README.md'),
    python_requires='>=3.8',
    zip_safe=True,
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_file('requirements/dev.txt').splitlines(),
    tests_require=read_file('requirements/test.txt').splitlines()[1:],
    setup_requires=['setuptools_scm', 'pytest-runner'],
    use_scm_version=True,
)
