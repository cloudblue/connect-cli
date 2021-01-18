# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, CloudBlue
# All rights reserved.
#

from cnct import ClientError


def generate(client, parameters, progress_callback):
    raise ClientError(
        message="Test",
        status_code=409,
        error_code=409,
        errors=[
            "some error"
        ]
    )
