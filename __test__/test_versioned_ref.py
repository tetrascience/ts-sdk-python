import sys
import os
import pytest

from ts_sdk.task.__util_versioned_ref import VersionedRef


def test_reconstructs_composite_ref():
    ref = VersionedRef(namespace="common", name="some-task", version="v1.0.0")
    assert ref == VersionedRef(
        composite="common/some-task:v1.0.0",
        namespace="common",
        name="some-task",
        version="v1.0.0",
    )


def test_decomposes_composite_ref():
    ref = VersionedRef(composite="common/some-task:v1.0.0")
    assert ref == VersionedRef(
        composite="common/some-task:v1.0.0",
        namespace="common",
        name="some-task",
        version="v1.0.0",
    )


def validates_ref_components():
    with pytest.raises(ValueError, match="inconsistent namespace"):
        VersionedRef(composite="common/some-task:v1.0.0", namespace="bad")

    with pytest.raises(ValueError, match="inconsistent name"):
        VersionedRef(composite="common/some-task:v1.0.0", name="bad")

    with pytest.raises(ValueError, match="inconsistent version"):
        VersionedRef(composite="common/some-task:v1.0.0", version="bad")
