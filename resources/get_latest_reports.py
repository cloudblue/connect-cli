import os
import shutil
import subprocess


CONNECT_REPORTS_REPO_URL = 'https://github.com/cloudblue/connect-reports.git'


BASE_DIR = os.path.abspath(
    os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
        ),
    ),
)


REPO_EMBED_DIR = os.path.join(
    BASE_DIR,
    'connect/.data/connect_reports',
)


def get_latest_reports():
    if os.path.exists(REPO_EMBED_DIR):
        shutil.rmtree(REPO_EMBED_DIR)

    print(f'Cloning {CONNECT_REPORTS_REPO_URL}...')

    subprocess.check_call(
        [
            'git',
            'clone',
            CONNECT_REPORTS_REPO_URL,
            REPO_EMBED_DIR,
        ],
    )

    result = subprocess.run(
        [
            'git', '-C', REPO_EMBED_DIR,
            'rev-list', '--tags', '--max-count=1',
        ],
        capture_output=True,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    result.check_returncode()
    commit_id = result.stdout.decode().replace('\n', '')

    print(f'Checkout latest tag ({commit_id})...')

    subprocess.check_call(
        [
            'git',
            '-C',
            REPO_EMBED_DIR,
            'checkout',
            commit_id,
        ],
    )

    print(f'Latest reports saved in {REPO_EMBED_DIR}')


if __name__ == '__main__':
    get_latest_reports()
