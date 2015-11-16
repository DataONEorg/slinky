import pytest

from d1lod import sesame

def test_interface_can_be_created(interface):
    assert isinstance(interface, sesame.Interface)
