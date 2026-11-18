"""The health endpoint must report the running version: that is how a deploy is verified."""

import pytest


@pytest.mark.parametrize("version", ["dev", "0.1.0", "1.4.2"])
def test_health_expone_la_version_desplegada(client, settings, version):
    settings.APP_VERSION = version
    r = client.get("/health/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": version}
