# -*- coding: utf-8 -*-
#
# Copyright (c) {% now 'utc', '%Y' %}, {{ cookiecutter.author }}
# All rights reserved.

def generate(
    client=None,
    input_data=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    """
    Extracts data from Connect using the ConnectClient instance
    and input data provided as arguments, applies
    required transformations (if any) and returns the data rendered
    by the given renderer on the arguments list.
    Some renderers may require extra context data to generate the report
    output, for example in the case of the Jinja2 renderer...

    :param client: An instance of the CloudBlue Connect
                    client.
    :type client: cnct.ConnectClient
    :param input_data: Input data used to calculate the
                        resulting dataset.
    :type input_data: dict
    :param progress_callback: A function that accepts t
                                argument of type int that must
                                be invoked to notify the progress
                                of the report generation.
    :type progress_callback: func
    :param renderer_type: Renderer required for generating report
                            output.
    :type renderer_type: string
    :param extra_context_callback: Extra content required by some
                            renderers.
    :type extra_context_callback: dict
    """
    pass
