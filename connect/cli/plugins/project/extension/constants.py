#  Copyright © 2021 CloudBlue. All rights reserved.


PYPI_EXTENSION_RUNNER_URL = 'https://pypi.org/pypi/connect-extension-runner/json'

PRE_COMMIT_HOOK = """#! /bin/sh

set -e

if [ -f /usr/local/bin/extension-check-static ]; then
    exec /usr/local/bin/extension-check-static {package_name}
else
    exec docker-compose run -T {project_slug}_bash /usr/local/bin/extension-check-static {package_name}
fi
"""
