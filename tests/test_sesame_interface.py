import pytest

from d1lod.sesame import interface as sesint

def test_interface_can_be_created(interface):
    assert isinstance(interface, sesint.SesameInterface)
