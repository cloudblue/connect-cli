#  Copyright © 2021 CloudBlue. All rights reserved.

PROJECT_REPORT_BOILERPLATE_URL = 'https://github.com/cloudblue/connect-report-python-boilerplate.git'
PROJECT_EXTENSION_BOILERPLATE_URL = 'https://github.com/cloudblue/connect-extension-python-boilerplate.git'

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
    'tier_config_setup_request_validation': 'validate_tier_config_setup_request',
    'tier_config_change_request_validation': 'validate_tier_config_change_request',
}

CAPABILITY_ALLOWED_STATUSES = [
    'approved',
    'draft',
    'failed',
    'inquiring',
    'pending',
    'tiers_setup',
]
