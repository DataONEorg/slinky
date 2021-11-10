from .conftest import client


def test_client(client):
    assert "default" in client.get_queues()
    assert "dataset" in client.get_queues()
