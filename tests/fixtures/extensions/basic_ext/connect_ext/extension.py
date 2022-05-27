# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Enterprise
# All rights reserved.
#
from connect.eaas.extension import (
    Extension,
)


class BasicExtension(Extension):
    def process_asset_purchase_request(self, request):
        pass

    def process_tier_config_setup_request(self, request):
        pass

    def execute_product_action(self, request):
        pass

    def process_product_custom_event(self, request):
        pass

    def execute_scheduled_processing(self, schedule):
        pass
