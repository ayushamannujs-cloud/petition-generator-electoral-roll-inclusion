"""The intake model — answers to the questionnaire that drive the petition.

Mirrors `one more time/intake-form.md`. Core slice: independent particulars
(3a) only; narrative beats and triggered law (3b/4b) arrive in later cycles.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Appeal must be filed within this window of the deletion (intake-form Q17).
APPEAL_WINDOW_DAYS = 15


def _parse_date(value: str) -> date | None:
    """Accept dd.mm.yyyy, dd/mm/yyyy, or ISO; return None if unrecognised."""
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None

Gender = Literal["male", "female", "other"]
# Why the appellant moved. Marriage and a plain transfer plead differently, so
# there is no safe default — the reason is required once a move is pleaded.
AddressChangeReason = Literal["marriage", "transfer"]


class Relative(BaseModel):
    name: str
    relationship: str
    epic_no: str | None = None


class PetitionInput(BaseModel):
    # Section A — who you are (3a independent particulars)
    appellant_name: str = Field(..., description="Full name as on EPIC")
    guardian_name: str | None = Field(None, description="Father's / Husband's name")
    gender: Gender = "female"
    address: str | None = None
    epic_no: str | None = None
    # Intake-only: the settled petition carries no contact line, so this is
    # captured so a volunteer can reach the appellant, never rendered.
    contact: str | None = None

    # Section B — forum & roll location (3a, derived)
    tribunal_venue: str | None = Field(
        None, description="Where the tribunal sits, e.g. 'Entally Jessop Building'"
    )
    district: str | None = None
    constituency_name: str | None = None
    constituency_no: str | None = None
    part_or_serial_no: str | None = None

    # Section C — narrative arc beats (each on/off; "on" reveals date/number)
    on_draft_roll: bool = False
    draft_roll_date: str | None = None
    enumeration_form_submitted: bool = False
    notice_received: bool = False
    notice_no: str | None = None
    notice_date: str | None = None
    notice_reason: str | None = None
    hearing_attended: bool = False
    hearing_officer: str | None = None
    hearing_date: str | None = None
    under_adjudication: bool = False
    final_roll_date: str | None = None
    deleted: bool = False
    deletion_date: str | None = None
    prior_notice_before_deletion: bool = True  # No strengthens PNJ
    appeal_filed: bool = False
    appeal_no: str | None = None
    appeal_date: str | None = None

    # Section D — documents held (3a list + 3b triggers)
    has_voter_id: bool = False
    has_aadhaar: bool = False
    aadhaar_no: str | None = None
    has_passport: bool = False
    passport_no: str | None = None
    has_pan: bool = False
    has_gst: bool = False
    other_documents: list[str] = Field(default_factory=list)

    # Section E — special legal triggers (3b → 4b) and switches
    mapped_2002_sir: bool = False
    relatives_on_roll: list[Relative] = Field(default_factory=list)
    continuous_resident_since: str | None = None

    # Section H — why the roll and the appellant's documents disagree.
    # A multi-select, like the documents held: more than one can apply at once.
    mismatch_appellant_name: bool = False
    name_on_roll: str | None = Field(None, description="Name as printed on the roll")
    mismatch_father_name: bool = False
    father_name_on_roll: str | None = None
    address_changed: bool = False
    address_change_reason: AddressChangeReason | None = None
    previous_address: str | None = None
    previous_constituency: str | None = None
    registered_since: str | None = None
    marriage_date: str | None = None
    spouse_name: str | None = Field(None, description="Husband's name, where the move follows marriage")
    other_reason: str | None = Field(None, description="Free text — where the listed reasons do not fit")

    # Section F — hardship & relief
    hardship: str | None = None
    relief_set_aside: bool = True
    relief_restore: bool = True
    relief_interim_vote: bool = True
    relief_compensation: bool = False

    # Section G — declaration
    place: str | None = None
    declaration_date: str | None = None

    @model_validator(mode="after")
    def _check_constraints(self) -> "PetitionInput":
        # Compensation relief is valid only where hardship is pleaded.
        if self.relief_compensation and not self.hardship:
            raise ValueError(
                "relief_compensation requires a hardship description"
            )
        # A pleaded move must say which kind: the two produce different sentences
        # and different legal weight, so guessing between them is not safe.
        if self.address_changed and not self.address_change_reason:
            raise ValueError(
                "address_change_reason is required when address_changed is set "
                "('marriage' or 'transfer')"
            )
        # Appeal must fall within APPEAL_WINDOW_DAYS of the deletion.
        if self.appeal_date and self.deletion_date:
            appeal = _parse_date(self.appeal_date)
            deletion = _parse_date(self.deletion_date)
            if appeal and deletion:
                if appeal < deletion:
                    raise ValueError("appeal_date cannot precede deletion_date")
                if appeal > deletion + timedelta(days=APPEAL_WINDOW_DAYS):
                    raise ValueError(
                        f"appeal_date must be within {APPEAL_WINDOW_DAYS} days "
                        f"of deletion_date"
                    )
        return self
