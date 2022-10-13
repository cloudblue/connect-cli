import configparser
import contextlib
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

import requests
import toml


RES_DIR = os.path.abspath(os.path.dirname(__file__))


@contextlib.contextmanager
def build_dir(dir):
    cwd = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(cwd)


def get_package_info(pkg_name):
    url = f'https://pypi.org/pypi/{pkg_name}/json'
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    res.raise_for_status()


def get_wheels_and_sdists():  # noqa: CCR001
    wheels = set()
    sdists = set()
    print('analyzing requirements.txt....')
    with open(os.path.join(RES_DIR, 'requirements.txt'), 'r') as f:
        for line in f:
            if ';' in line:
                package_with_ver, _ = line.split(';')
            else:
                package_with_ver = line.replace('\n', '')
            package, version = package_with_ver.split('==')
            pkg_info = get_package_info(package)
            required_version = pkg_info['releases'][version.strip()]
            sdist_url = None
            for pkg_file_info in required_version:
                if (
                    pkg_file_info['packagetype'] == 'bdist_wheel'
                    and (
                        'win_amd64' in pkg_file_info['filename']
                        or 'any' in pkg_file_info['filename']
                    )
                ):
                    wheels.add(package_with_ver)
                    break
                if pkg_file_info['packagetype'] == 'sdist':
                    sdist_url = pkg_file_info['url']
            else:
                if sdist_url:
                    print(f'Package {package} has no wheel')
                    sdists.add(sdist_url)
    return wheels, sdists


def download_and_build_missing_wheels(sdists):
    for sdist in sdists:
        _, filename = sdist.rsplit('/', 1)
        print(f'Download source distribution {filename}...')
        with tempfile.TemporaryDirectory() as tmpdir:
            with requests.get(sdist, stream=True) as r:
                dest_name = os.path.join(tmpdir, filename)
                with open(dest_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            if filename.endswith('gz'):
                with tarfile.open(dest_name, 'r:gz') as tarf:
                    tarf.extractall(tmpdir)
            if filename.endswith('zip'):
                with zipfile.ZipFile(dest_name, 'r') as zipf:
                    zipf.extractall(tmpdir)
            os.unlink(dest_name)
            libdir = os.path.join(tmpdir, os.listdir(tmpdir)[0])
            with build_dir(libdir):
                print('generate wheel....')
                if os.path.exists(os.path.join(libdir, 'setup.py')):
                    subprocess.check_call(['python', 'setup.py', 'bdist_wheel'])
                elif os.path.exists(os.path.join(libdir, 'pyproject.toml')):
                    subprocess.check_call(['poetry', 'build', '--format', 'wheel'])
                wheel = os.listdir(os.path.join(libdir, 'dist'))[0]
                print(f'Move generated wheel {wheel} to resources')
                shutil.move(
                    os.path.join(libdir, 'dist', wheel),
                    os.path.join(RES_DIR, wheel),
                )


def write_conf(wheels):
    pyproject = toml.load(os.path.join(RES_DIR, '../pyproject.toml'))
    config = configparser.RawConfigParser()
    general = pyproject['tool']['poetry']
    entry_point = general['scripts']['ccli']
    config['Application'] = {
        'name': general['description'],
        'version': general['version'],
        'publisher': ', '.join(general['authors']),
        'license_file': '../LICENSE',
        'console': 'true',
        'target': '$SYSDIR\\WindowsPowerShell\\v1.0\\powershell.exe',
        'parameters': '-noexit -ExecutionPolicy Bypass -File "$INSTDIR\\ccli_shell.ps1"',
        'icon': 'connect.ico',
    }
    config['Python'] = {
        'version': '3.8.10',
        'bitness': '64',
    }
    config['Include'] = {
        'pypi_wheels': '\n'.join(wheels),
        'local_wheels': '*.whl',
        'files': 'ccli_shell.ps1',
    }
    config['Command ccli'] = {
        'entry_point': entry_point,
    }
    config['Build'] = {
        'installer_name': f'connect-cli_{general["version"]}_setup.exe',
    }

    with open(os.path.join(RES_DIR, 'ccli.cfg'), 'w') as f:
        config.write(f)

    print('pynsist config file written!')


def generate():
    wheels, sdists = get_wheels_and_sdists()
    wheels.add('setuptools==59.6.0')
    download_and_build_missing_wheels(sdists)
    write_conf(wheels)


if __name__ == '__main__':
    generate()
