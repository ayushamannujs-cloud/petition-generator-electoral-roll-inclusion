"""Cross-field validations (intake-form.md [validate] tags)."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.intake import PetitionInput


def base(**kw) -> PetitionInput:
    return PetitionInput(appellant_name="Priya Devi Das", gender="female", **kw)


def test_appeal_within_15_days_is_valid():
    # 27.03.2026 deletion -> appeal on 04.04.2026 is 8 days later: OK.
    base(
        appeal_filed=True,
        deleted=True,
        deletion_date="27.03.2026",
        appeal_date="04.04.2026",
    )


def test_appeal_beyond_15_days_is_rejected():
    with pytest.raises(ValidationError):
        base(
            appeal_filed=True,
            deleted=True,
            deletion_date="27.03.2026",
            appeal_date="20.04.2026",  # 24 days later
        )


def test_compensation_without_hardship_is_rejected():
    with pytest.raises(ValidationError):
        base(relief_compensation=True, hardship=None)


def test_compensation_with_hardship_is_valid():
    base(relief_compensation=True, hardship="elderly and unwell")
