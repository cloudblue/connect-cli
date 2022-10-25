#  Copyright © 2021 CloudBlue. All rights reserved.


CAPABILITY_METHOD_MAP = {
    'asset_purchase_request_processing': 'process_asset_purchase_request',
    'asset_change_request_processing': 'process_asset_change_request',
    'asset_suspend_request_processing': 'process_asset_suspend_request',
    'asset_resume_request_processing': 'process_asset_resume_request',
    'asset_cancel_request_processing': 'process_asset_cancel_request',
    'asset_adjustment_request_processing': 'process_asset_adjustment_request',
    'asset_purchase_request_validation': 'validate_asset_purchase_request',
    'asset_change_request_validation': 'validate_asset_change_request',
    'product_action_execution': 'execute_product_action',
    'product_custom_event_processing': 'process_product_custom_event',
    'tier_config_setup_request_processing': 'process_tier_config_setup_request',
    'tier_config_change_request_processing': 'process_tier_config_change_request',
    'tier_config_adjustment_request_processing': 'process_tier_config_adjustment_request',
    'tier_config_setup_request_validation': 'validate_tier_config_setup_request',
    'tier_config_change_request_validation': 'validate_tier_config_change_request',
    'usage_file_request_processing': 'process_usage_file',
    'part_usage_file_request_processing': 'process_usage_chunk_file',
    'tier_account_update_request_processing': 'process_tier_account_update_request',
}

CAPABILITY_ALLOWED_STATUSES = [
    'approved',
    'draft',
    'failed',
    'inquiring',
    'pending',
    'tiers_setup',
]

REQUESTS_SCHEDULED_ACTION_STATUSES = [
    'scheduled',
    'revoking',
    'revoked',
]

STATUSES = [
    'draft',
    'tiers_setup',
    'pending',
    'inquiring',
    'approved',
    'failed',
]

REQUESTS_SCHEDULED_ACTION_STATUSES = [
    'scheduled',
    'revoking',
    'revoked',
]

TIER_ACCOUNT_UPDATE_STATUSES = [
    'pending',
    'accepted',
    'ignored',
]

USAGE_FILE_STATUSES = [
    'draft',
    'uploading',
    'uploaded',
    'invalid',
    'processing',
    'ready',
    'rejected',
    'pending',
    'accepted',
    'closed',
]

CHUNK_FILE_STATUSES = [
    'draft',
    'ready',
    'closed',
    'failed',
]


PYPI_EXTENSION_RUNNER_URL = 'https://pypi.org/pypi/connect-extension-runner/json'


VALIDATION_RESULTS_HEADER = """
| Field | Value |
|:------|-------|
"""


PRE_COMMIT_HOOK = """#!/usr/bin/env python
import subprocess
import sys


print('\\n\\033[0;34m\\u2022 Building static assets [ ]\\033[0m', end='')

result = subprocess.run(
    'npm run build',
    shell=True,
    capture_output=True,
)

if result.returncode != 0:
    print('\\r\\033[0;34m\\u2022 Building static assets [\\033[0;31m\\u2717\\033[0;34m]\\033[0m\\n')
    if result.stdout:
        print(result.stdout.decode())
    if result.stderr:
        print(result.stderr.decode())
    sys.exit(1)


print('\\r\\033[0;34m\\u2022 Building static assets [\\033[0;32m\\u2713\\033[0;34m]\\033[0m')

print('\\033[0;34m\\u2022 Check untracked static assets [ ]\\033[0m', end='')

result = subprocess.run(
    'git status --porcelain {package_name}/static',
    capture_output=True,
    shell=True,
)

if result.returncode != 0:
    print('\\r\\033[0;34m\\u2022 Check untracked static assets [\\033[0;31m\\u2717\\033[0;34m]\\033[0m\\n')
    if result.stdout:
        print(result.stdout.decode())
    if result.stderr:
        print(result.stderr.decode())
    sys.exit(1)

out = result.stdout.decode()
untracked = [line[3:] for line in out.splitlines() if line.startswith('??')]

if untracked:
    print('\\r\\033[0;34m\\u2022 Check untracked static assets [\\033[0;31m\\u2717\\033[0;34m]\\033[0m\\n')
    print('\\033[0;31mUntracked static assets:\\033[0m')
    for line in untracked:
        print('\\t' + line)
    print('')
    sys.exit(1)

print('\\r\\033[0;34m\\u2022 Check untracked static assets [\\033[0;32m\\u2713\\033[0;34m]\\033[0m\\n')
"""
