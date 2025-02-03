"""
SPDX-FileCopyrightText: © Sebastian Thomschke and contributors
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-ArtifactOfProjectHomePage: https://github.com/Second-Hand-Friends/kleinanzeigen-bot/
"""
import pytest
from kleinanzeigen_bot import utils


def test_ensure() -> None:
    utils.ensure(True, "TRUE")
    utils.ensure("Some Value", "TRUE")
    utils.ensure(123, "TRUE")
    utils.ensure(-123, "TRUE")
    utils.ensure(lambda: True, "TRUE")

    with pytest.raises(AssertionError):
        utils.ensure(False, "FALSE")

    with pytest.raises(AssertionError):
        utils.ensure(0, "FALSE")

    with pytest.raises(AssertionError):
        utils.ensure("", "FALSE")

    with pytest.raises(AssertionError):
        utils.ensure(None, "FALSE")

    with pytest.raises(AssertionError):
        utils.ensure(lambda: False, "FALSE", timeout = 2)


def test_calculate_content_hash_with_none_values() -> None:
    """Test calculate_content_hash with None values in the ad configuration."""
    ad_cfg = {
        # Minimale Konfiguration mit None-Werten wie im Bug-Report beschrieben
        "id": "123456789",
        "created_on": "2022-07-19T07:30:20.489289",
        "updated_on": "2025-01-22T19:46:46.735896",
        "title": "Test Anzeige",
        "description": "Test Beschreibung",
        "images": [None, "/path/to/image.jpg", None],  # None-Werte in der images Liste
        "shipping_options": None,  # None statt Liste
        "special_attributes": None,  # None statt Dictionary
        "contact": {
            "street": None  # None-Wert in contact
        }
    }

    # Sollte keinen TypeError werfen
    hash_value = utils.calculate_content_hash(ad_cfg)
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64  # SHA-256 Hash ist 64 Zeichen lang
