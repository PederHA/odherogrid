import random

import pytest

from odherogrid.resources import _get_new_category

def test__get_new_category():
    arg = lambda: random.uniform(-3840, 3840)
    kwargs = ["x_pos", "y_pos", "width", "height"]
    for i in range(50):
        assert _get_new_category("test", x_pos=arg())
        assert _get_new_category("test", y_pos=arg())
        assert _get_new_category("test", width=arg())
        assert _get_new_category("test", height=arg())
        
        # Test random combination (and number) of keywords
        random.shuffle(kwargs)
        kw = kwargs[0:random.randint(1, len(kwargs))]
        params = {k: arg() for k in kw}
        assert _get_new_category("test", **params)