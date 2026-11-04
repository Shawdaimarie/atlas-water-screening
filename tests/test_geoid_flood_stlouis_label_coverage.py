from __future__ import annotations

import numpy as np
import pytest

from scripts.audit_geoid_flood_stlouis_labels import class_summary


def test_class_summary_separates_mapped_labels_from_outside_map_pixels():
    result = class_summary(np.array([0, 0, 1, 2, 255], dtype=np.uint8))

    assert result["pixel_count"] == 5
    assert result["class_counts"] == {"0": 2, "1": 1, "2": 1, "255": 1}
    assert result["mapped_label_pixels"] == 4
    assert result["mapped_label_fraction"] == 0.8
    assert result["flooded_water_pixels"] == 1
    assert result["outside_map_pixels"] == 1


@pytest.mark.parametrize("pixels", [np.array([], dtype=np.uint8), np.array([[0, 1]], dtype=np.uint8)])
def test_class_summary_rejects_empty_or_non_vector_input(pixels):
    with pytest.raises(ValueError):
        class_summary(pixels)


def test_class_summary_rejects_unrecognized_classes():
    with pytest.raises(ValueError, match="Unexpected GEOID-Flood label classes"):
        class_summary(np.array([3], dtype=np.uint8))
