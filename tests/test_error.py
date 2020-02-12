from odherogrid.error import get_stack_frames

def test_get_stack_frames():
    assert next(get_stack_frames())
    for frame in get_stack_frames():
        assert frame
