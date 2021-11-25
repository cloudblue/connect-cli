#  Copyright © 2021 CloudBlue. All rights reserved.
import os


PROJECT_EXTENSION_BOILERPLATE_URL = 'https://github.com/cloudblue/connect-extension-python-boilerplate.git'
PROJECT_EXTENSION_BOILERPLATE_TAG = os.environ.get('PROJECT_EXTENSION_BOILERPLATE_TAG')

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
    'listing_new_request_processing': 'process_new_listing_request',
    'listing_remove_request_processing': 'process_remove_listing_request',
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

LISTING_REQUEST_STATUSES = [
    'draft',
    'reviewing',
    'deploying',
    'canceled',
    'completed',
]

USAGE_FILE_STATUSES = [
    'draft',
    'uploading',
    'uploaded',
    'invalid',
    'processing',
    'processed',
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
