# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
import os

import pytest

from connect.cli.plugins.play.context import Context
from connect.cli.plugins.play.save import Save


def test_context(fs):
    context_src = """{
    "endpoint": "https://api.cnct.info/public/v1",
    "program_agreement_id": "AGP-927-440-678",
    "distribution_agreements": [
        "AGD-199-236-391",
        "AGD-669-983-907"
    ],
    "program_contract_id": "CRP-41033-36725-76650",
    "vendor_account_id": "VA-677-276"
}"""

    dir = os.path.join(fs.root_path, 'play')
    os.makedirs(dir, exist_ok=True)

    cfile = os.path.join(dir, 'context.json')
    sfile = os.path.join(dir, 'updated.json')
    nofile = os.path.join(dir, 'nonexistent.json')

    with open(cfile, 'w') as f:
        print(context_src, file=f)

    ctx = Context.create_from_file(filename=cfile)
    assert ctx.program_agreement_id == 'AGP-927-440-678'
    assert ctx.program_contract_id == 'CRP-41033-36725-76650'
    assert len(ctx.distribution_agreements) == 2
    assert str(ctx) == context_src

    ctx = Context.create_from_file(filename=nofile)
    assert len(ctx) == 0

    ctx = Context.create(filename=cfile)
    assert ctx.program_agreement_id == 'AGP-927-440-678'
    assert ctx.program_contract_id == 'CRP-41033-36725-76650'
    assert len(ctx.distribution_agreements) == 2
    assert str(ctx) == context_src

    ctx = Context.create(filename=nofile)
    assert len(ctx) == 0

    ctx = Context.create(args=['program_agreement_id=AGP-xxx-xxx-xxx'], filename=cfile)
    assert ctx.program_agreement_id == 'AGP-xxx-xxx-xxx'
    assert str(ctx) != context_src

    ctx = Context.create(program_agreement_id='AGP-yyy-yyy-yyy', filename=cfile)
    assert ctx.program_agreement_id == 'AGP-yyy-yyy-yyy'
    assert str(ctx) != context_src

    ctx = Context.create(program_contract_id=None, filename=cfile)
    assert ctx.program_contract_id == 'CRP-41033-36725-76650'
    assert str(ctx) == context_src

    ctx = Context.create(filename=cfile)
    ctx.program_agreement_id = 'AGP-123-456-789'
    ctx.save(filename=sfile)

    xtx = Context.create(filename=sfile)
    assert str(xtx) == str(ctx)

    with pytest.raises(KeyError):
        ctx = Context.create(filename=None)
        type(ctx.nonexistent)

    ctx = Context.create(filename=cfile)
    ctx |= ('distribution_agreements', 'AGD-999-999-999')
    assert ctx.distribution_agreements == ['AGD-199-236-391', 'AGD-669-983-907', 'AGD-999-999-999']

    ctx = Context.create(filename=cfile)
    ctx |= ('distribution_agreements_x', 'AGD-999-999-999')
    assert ctx.distribution_agreements_x == ['AGD-999-999-999']

    ctx = Context.create(filename=cfile)
    ctx |= ('distribution_agreements_x', ['AGD-999-999-999', 'AGD-999-999-000'])
    assert ctx.distribution_agreements_x == ['AGD-999-999-999', 'AGD-999-999-000']

    ctx = Context.create(filename=cfile)
    ctx |= ('kdict', {'a': 'AGD-999-999-999'})
    assert ctx.kdict == {'a': 'AGD-999-999-999'}
    ctx |= ('kdict', {'b': 'AGD-999-999-000'})
    assert ctx.kdict == {'a': 'AGD-999-999-999', 'b': 'AGD-999-999-000'}

    ctx = Context.create(filename=cfile)
    Context.context_file_name = sfile
    ctx | Save
    ctx | Save()
