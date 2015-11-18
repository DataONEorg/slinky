import pytest

from d1lod.sesame import Store, Repository, Interface
from d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)
