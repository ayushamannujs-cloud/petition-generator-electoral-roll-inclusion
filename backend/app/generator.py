"""The petition generator — pours an intake into a .docx document.

This is the deep module: a tiny public interface (`build_petition`) hiding the
layered assembly (scaffold → boilerplate → particulars → standing law).
Section order follows scaffold-rules.md §5; typography follows §1-4.
"""
from __future__ import annotations

import docx
from docx.document import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from app.intake import PetitionInput

# Gender-driven vocabulary (intake-form.md Q3 — drives every pronoun).
_RELATION = {"male": "son of", "female": "daughter of", "other": "child of"}
_SPOUSE_RELATION = {"male": "husband of", "female": "wife of", "other": "spouse of"}
_SUBJECT = {"male": "he", "female": "she", "other": "they"}
_POSSESSIVE = {"male": "his", "female": "her", "other": "their"}

# Typography (scaffold-rules.md §2-4).
_FONT = "Bookman Old Style"
_BODY_PT = Pt(12)
_BODY_SPACING = 1.5

_ALIGN = {
    "heading": WD_ALIGN_PARAGRAPH.CENTER,   # structural marker
    "body": WD_ALIGN_PARAGRAPH.JUSTIFY,     # argument
    "party": WD_ALIGN_PARAGRAPH.RIGHT,      # party label
    "left": WD_ALIGN_PARAGRAPH.LEFT,        # district line
}

# Placement, measured off the settled petition (offsets from the text margin).
# The cause title, the party block and the whole prayer sit in a right-hand
# column; numbered paragraphs hang, with submissions set one step deeper.
_RIGHT_COLUMN = Inches(2.75)
_HANGING = Inches(0.25)
_SUBMISSION_TAB = Inches(0.5)
_QUOTE = Inches(0.75)      # quoted matter, e.g. the notice text
_CONTINUATION = Inches(0.5)  # prose continuing a numbered paragraph


class _Counter:
    """The single arabic run shared by facts, grounds and submissions.

    Numbers are counted as paragraphs are emitted rather than written into the
    text, so a paragraph that does not fire leaves no gap behind it.
    """

    def __init__(self) -> None:
        self._n = 0

    def next(self) -> int:
        self._n += 1
        return self._n


def build_petition(intake: PetitionInput) -> Document:
    doc = docx.Document()
    counter = _Counter()
    _apply_page_geometry(doc)
    _district_line(doc, intake)
    _forum(doc, intake)
    _cause_title(doc, intake)
    _respondents(doc, intake)
    _preamble(doc, intake)
    _facts(doc, intake, counter)
    _documents(doc, intake, counter)
    _entitlement(doc, intake, counter)
    _relatives(doc, intake, counter)
    _grounds(doc, intake, counter)
    _submissions(doc, intake, counter)
    _closing_tag(doc, counter)
    _prayer(doc, intake)
    _declaration(doc, intake)
    _verification(doc, intake)
    _enclosures(doc, intake)
    return doc


# --- typography primitives ---------------------------------------------------

def _apply_page_geometry(doc: Document) -> None:
    sec = doc.sections[0]
    # A4 portrait.
    sec.page_width = Inches(8.2677)   # 210 mm
    sec.page_height = Inches(11.6929)  # 297 mm
    # Asymmetric margins: left & top get the extra half-inch (§1).
    sec.left_margin = Inches(1.5)
    sec.top_margin = Inches(1.5)
    sec.right_margin = Inches(1)
    sec.bottom_margin = Inches(1)


def _p(
    doc: Document,
    text: str,
    role: str = "body",
    *,
    bold: bool = False,
    left_indent=None,
    first_line_indent=None,
    tab_stop=None,
):
    para = doc.add_paragraph()
    para.alignment = _ALIGN[role]
    fmt = para.paragraph_format
    if role == "body":
        fmt.line_spacing = _BODY_SPACING
    if left_indent is not None:
        fmt.left_indent = left_indent
    if first_line_indent is not None:
        fmt.first_line_indent = first_line_indent
    if tab_stop is not None:
        fmt.tab_stops.add_tab_stop(tab_stop)
    run = para.add_run(text)
    run.font.name = _FONT
    run.font.size = _BODY_PT
    run.bold = bold or role == "heading"
    return para


def _numbered(doc: Document, counter: _Counter, text: str, *, deep: bool = False):
    """A paragraph in the arabic run — takes the next number as it is emitted.

    `deep` sets the text a further quarter-inch in, after a tab: the settled
    petition distinguishes submissions from facts by that indent alone.
    """
    number = counter.next()
    if deep:
        return _p(
            doc,
            f"{number}.\t{text}",
            left_indent=_HANGING,
            first_line_indent=-_HANGING,
            tab_stop=_SUBMISSION_TAB,
        )
    return _p(
        doc,
        f"{number}. {text}",
        left_indent=_HANGING,
        first_line_indent=-_HANGING,
    )


# --- scaffold sections -------------------------------------------------------

def _district_line(doc: Document, intake: PetitionInput) -> None:
    district = (intake.district or "____").upper()
    _p(doc, f"DISTRICT: {district}", "left", bold=True)


def _forum(doc: Document, intake: PetitionInput) -> None:
    """Three centred lines, as the settled petition heads the page."""
    _p(doc, "BEFORE THE HON'BLE SIR APPELLATE TRIBUNAL FOR", "heading")
    _p(doc, "ELECTORAL ROLLS (SIR 2026)", "heading")
    _p(doc, (intake.tribunal_venue or "____").upper(), "heading")


def _cause_title(doc: Document, intake: PetitionInput) -> None:
    """The right-hand column: everything identifying the matter and the parties."""
    epic = intake.epic_no or "____"
    appeal_no = intake.appeal_no or "____"
    appeal_date = intake.appeal_date or "____"
    roll_date = intake.deletion_date or "____"
    _p(doc, "IN THE MATTER OF:", left_indent=_RIGHT_COLUMN)
    _p(
        doc,
        f"In the matter of Appeal no {appeal_no} submitted online on date "
        f"{appeal_date} challenging the deletion of voter bearing EPIC No. "
        f"{epic} in the roll dated {roll_date}.",
        left_indent=_RIGHT_COLUMN,
    )
    _p(doc, "AND", "heading", left_indent=_RIGHT_COLUMN)
    _p(doc, "IN THE MATTER OF", left_indent=_RIGHT_COLUMN)
    guardian = intake.guardian_name or "____"
    relation = _RELATION[intake.gender]
    address = intake.address or "____"
    # The married name is the same datum as the marriage clause in ¶1; it is
    # stated here too because the settled petition identifies the appellant by
    # both her father and her husband.
    spouse = (
        f"{_SPOUSE_RELATION[intake.gender]} {intake.spouse_name}, "
        if intake.spouse_name
        else ""
    )
    _p(
        doc,
        f"1. {intake.appellant_name}, {relation} {guardian}, "
        f"{spouse}residing at {address}.",
        left_indent=_RIGHT_COLUMN,
    )
    _p(doc, "………. Appellant", "party")


def _respondents(doc: Document, intake: PetitionInput) -> None:
    # Centred within the column rather than the page — the settled petition puts
    # VERSUS at x≈414pt, the midpoint of the right-hand column, not of the sheet.
    _p(doc, "VERSUS", "heading", left_indent=_RIGHT_COLUMN)
    constituency = intake.constituency_name or "____"
    district = intake.district or "____"
    _p(
        doc,
        "1. The Election Commission of India, Nirvachan Sadan, Ashoka Road, "
        "New Delhi-110001.",
        left_indent=_RIGHT_COLUMN,
    )
    _p(
        doc,
        f"2. The Electoral Registration Officer (ERO), {constituency} Assembly "
        f"Constituency.",
        left_indent=_RIGHT_COLUMN,
    )
    _p(
        doc,
        f"3. The District Election Officer (DEO), {district}.",
        left_indent=_RIGHT_COLUMN,
    )
    # Singular in the settled petition, despite there being three of them.
    _p(doc, "………. Respondent", "party")


def _preamble(doc: Document, intake: PetitionInput) -> None:
    appeal_no = intake.appeal_no or "____"
    order_date = intake.deletion_date or "____"
    _p(
        doc,
        f"Supplementing online application being No. {appeal_no}, submitting "
        f"herewith following facts, for the perusal of the Hon'ble Tribunal with "
        f"the attached documents for its appreciation to challenge the Order "
        f"dated {order_date} passed by the Designated Judicial Officer in respect "
        f"of the Appellant's exclusion from the Supplementary Electoral Roll.",
    )
    _p(doc, "MOST RESPECTFULLY SHEWETH:", bold=True)


def _facts(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    _residence(doc, intake, counter)
    _identity(doc, intake, counter)
    _other_reason(doc, intake, counter)
    _beats(doc, intake, counter)
    # Triggered law (4b) — passport unlocks the Passports Act inside the facts.
    if intake.has_passport:
        no = intake.passport_no or "____"
        _numbered(
            doc,
            counter,
            f"That the Appellant holds a valid Indian Passport bearing No. {no}, "
            f"which under the Passports Act, 1967 is conclusive proof of the "
            f"Appellant's citizenship and date of birth.",
        )


def _address_change_clause(intake: PetitionInput) -> str | None:
    """The move that explains the appellant's present address, if one is pleaded.

    A clause rather than a paragraph: the settled petition keeps residence and
    the move that produced it in a single ¶1.
    """
    if not intake.address_changed:
        return None
    subject = _SUBJECT[intake.gender].capitalize()
    possessive = _POSSESSIVE[intake.gender]
    previous = intake.previous_address or "____"
    tail = ""
    if intake.previous_constituency or intake.registered_since:
        constituency = intake.previous_constituency or "____"
        since = intake.registered_since or "____"
        tail = (
            f" and has been a registered voter in the West Bengal Electoral Rolls "
            f"of {constituency} assembly constituency since {since}"
        )
    if intake.address_change_reason == "marriage":
        spouse = intake.spouse_name or "____"
        date = intake.marriage_date or "____"
        return (
            f"{subject} shifted {possessive} residence permanently from {previous} "
            f"after marrying {spouse} on {date}{tail}."
        )
    return (
        f"{subject} shifted {possessive} residence permanently from "
        f"{previous}{tail}."
    )


def _residence(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """Settled petition ¶1 — where the Appellant lives, and how she came to."""
    clauses = [f"That the Appellant is a permanent resident of {intake.address or '____'}."]
    move = _address_change_clause(intake)
    if move:
        clauses.append(move)
    _numbered(doc, counter, " ".join(clauses))


def _name_variation_clauses(intake: PetitionInput) -> list[str]:
    """How the roll spells the appellant and her father, where it differs.

    Clauses on the identity paragraph rather than paragraphs of their own — the
    discrepancy is part of describing who the Appellant is, not a separate event.
    """
    clauses: list[str] = []
    if intake.mismatch_appellant_name:
        on_roll = intake.name_on_roll or "____"
        clauses.append(
            f"The Appellant's name is recorded in the said roll as {on_roll}, "
            f"whereas the Appellant's true name, as borne out by the documents "
            f"produced herewith, is {intake.appellant_name}."
        )
    if intake.mismatch_father_name:
        on_roll = intake.father_name_on_roll or "____"
        guardian = intake.guardian_name or "____"
        clauses.append(
            f"The name of the Appellant's father is recorded in the said roll as "
            f"{on_roll}, whereas it is {guardian}."
        )
    return clauses


def _identity(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """Settled petition ¶2 — citizenship, the EPIC, and the Article 326 mandate."""
    epic = intake.epic_no or "____"
    ac_name = intake.constituency_name or "____"
    ac_no = intake.constituency_no or "____"
    clauses = [
        f"That the Appellant, as an Indian citizen having attained the age of "
        f"majority, was issued a Voter Identity Card bearing EPIC No. {epic} by "
        f"the Election Commission of India pursuant to the mandate of Article 326 "
        f"of the Constitution of India, which provides for adult suffrage, and was "
        f"enrolled in the electoral roll of the {ac_name} Assembly Constituency "
        f"(AC No. {ac_no}), having at all material times complied with the "
        f"requirements of the Representation of the People Act, 1950."
    ]
    clauses.extend(_name_variation_clauses(intake))
    _numbered(doc, counter, " ".join(clauses))


def _other_reason(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """The escape hatch, where the listed reasons do not fit the appellant."""
    if not intake.other_reason:
        return
    _numbered(
        doc,
        counter,
        f"That the discrepancy in the electoral roll further arises from the "
        f"following circumstance: {intake.other_reason.strip().rstrip('.')}.",
    )


def _beats(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """Narrative arc — conditional beats in strict chronology (no beat, no line)."""
    if intake.on_draft_roll:
        date = intake.draft_roll_date or "____"
        # Two sentences, as the settled ¶3 has them; the first is pleaded only
        # where the appellant says they filed the enumeration form.
        clauses = []
        if intake.enumeration_form_submitted:
            clauses.append(
                "That the Appellant duly completed and submitted the enumeration "
                "form as provided by the Booth Level Officer."
            )
            clauses.append(
                f"Consequently the Appellant's name was formally incorporated and "
                f"featured in the Draft Electoral Roll published on {date}, thereby "
                f"establishing a prima facie recognition of the Appellant's "
                f"eligibility to be enrolled."
            )
        else:
            clauses.append(
                f"That the Appellant's name duly appeared in the Draft Electoral "
                f"Roll published on {date}, thereby establishing a prima facie "
                f"recognition of the Appellant's eligibility to be enrolled."
            )
        _numbered(doc, counter, " ".join(clauses))
    if intake.notice_received:
        no = intake.notice_no or "____"
        date = intake.notice_date or "____"
        subject = _SUBJECT[intake.gender]
        lead = (
            f"That despite the earlier inclusion of the Appellant's name in the "
            f"draft electoral roll, {subject} received a hearing notice bearing "
            f"Notice No.: {no} regarding the Special Intensive Revision (SIR) on "
            f"{date}"
        )
        if intake.notice_reason:
            # Quoted verbatim and set in, as the settled ¶4 sets the notice text.
            _numbered(doc, counter, f"{lead}, wherein, inter alia, it was stated that:")
            quoted = intake.notice_reason.strip().strip('"').strip()
            _p(doc, f'"{quoted}"', left_indent=_QUOTE)
        else:
            _numbered(doc, counter, f"{lead}.")
        if intake.hearing_officer:
            _p(
                doc,
                f"Vide the said Notice, the Appellant was asked to appear before "
                f"{intake.hearing_officer} along with the original documents "
                f"prescribed by the ECI to retain the Appellant's name in the "
                f"Final Electoral Roll.",
                left_indent=_CONTINUATION,
            )
    if intake.hearing_attended:
        officer = intake.hearing_officer or "____"
        date = intake.hearing_date or "____"
        _numbered(
            doc,
            counter,
            f"That the Appellant duly attended the hearing before {officer} on "
            f"{date} and submitted all documents in support of the Appellant's "
            f"claim, in the legitimate expectation of inclusion.",
        )
    if intake.under_adjudication:
        date = intake.final_roll_date or "28.02.2026"
        _numbered(
            doc,
            counter,
            f"That in the Final Electoral Roll published on {date}, the Appellant's "
            f"name was marked 'Under Adjudication'.",
        )
    if intake.deleted:
        date = intake.deletion_date or "____"
        rider = (
            " without any prior notice or hearing whatsoever"
            if not intake.prior_notice_before_deletion
            else ""
        )
        _numbered(
            doc,
            counter,
            f"That the Appellant's name was thereafter deleted vide a Supplementary "
            f"/ Deleted-Electors list dated {date}{rider}, which order is impugned "
            f"herein.",
        )
    if intake.appeal_filed:
        no = intake.appeal_no or "____"
        date = intake.appeal_date or "____"
        _numbered(
            doc,
            counter,
            f"That the Appellant has preferred the present online appeal bearing "
            f"No. {no} dated {date}, well within the period of limitation.",
        )


def _held_documents(intake: PetitionInput) -> list[tuple[str, str | None]]:
    """The documents the appellant holds, as (label, number) — feeds table + enclosures."""
    docs: list[tuple[str, str | None]] = []
    if intake.has_voter_id:
        docs.append(("Voter ID / EPIC card", intake.epic_no))
    if intake.has_aadhaar:
        docs.append(("Aadhaar", intake.aadhaar_no))
    if intake.has_passport:
        docs.append(("Passport", intake.passport_no))
    if intake.has_pan:
        docs.append(("PAN", None))
    if intake.has_gst:
        docs.append(("GST registration", None))
    docs.extend((other, None) for other in intake.other_documents)
    return docs


def _documents(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """3a + cascade-enclosure: a 'documents relied upon' table."""
    docs = _held_documents(intake)
    if not docs:
        return
    _numbered(
        doc,
        counter,
        "That the Appellant relies upon and produces the following documents in "
        "support of the Appellant's identity, citizenship and ordinary residence:",
    )
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    for cell, head in zip(table.rows[0].cells, ("#", "Document", "Number")):
        cell.paragraphs[0].add_run(head).bold = True
    for i, (label, number) in enumerate(docs, start=1):
        row = table.add_row().cells
        row[0].text = str(i)
        row[1].text = label
        row[2].text = number or "—"
    # Settled ¶9 closes here, unnumbered and back at the margin.
    _p(
        doc,
        "Leave is hereby craved to submit and rely on additional supporting "
        "documents at the time of hearing if necessary.",
    )


def _entitlement(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """Settled petition ¶10 — entitlement is pleaded as a fact, not argued as a ground.

    It closes the documents section: having produced the proofs, the Appellant
    says plainly that nothing disqualifies her.
    """
    _numbered(
        doc,
        counter,
        "That the Appellant being an Indian citizen and having attained majority "
        "and not being otherwise disqualified under the Representation of the "
        "People Act, 1951, the Appellant ought to have been included in the final "
        "electoral roll.",
    )


def _relatives(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """Switch: close relatives on the roll add a citizenship-corroboration block."""
    if not intake.relatives_on_roll:
        return
    _numbered(
        doc,
        counter,
        "That the following close relatives of the Appellant are currently "
        "enrolled in the electoral roll, which corroborates the Appellant's "
        "citizenship and ordinary residence within the constituency:",
    )
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    for cell, head in zip(table.rows[0].cells, ("Name", "Relationship", "EPIC No.")):
        cell.paragraphs[0].add_run(head).bold = True
    for rel in intake.relatives_on_roll:
        row = table.add_row().cells
        row[0].text = rel.name
        row[1].text = rel.relationship
        row[2].text = rel.epic_no or "—"
    # Settled ¶11 draws the inference in prose after the table. Third person,
    # though the settled draft slips into "me and my family".
    _p(
        doc,
        "The presence of the above relatives in the roll further shows that the "
        "Appellant and the Appellant's family are Indian citizens who have "
        "resided in India and West Bengal continuously for several years, and "
        "that the deletion of the Appellant's name from the electoral roll is "
        "unjustified and untenable in law.",
        left_indent=_HANGING,
    )


def _grounds(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """Why the prayers should be allowed — counsel's four, stated briefly.

    Standing law: these are the violations committed by the authority, and they
    do not vary with the appellant. Everything appellant-specific is a fact or a
    submission. The one triggered addition is the clerical variation ground,
    which a name mismatch pleaded in the facts fires.
    """
    _p(doc, "GROUNDS", "heading")
    hardship_rider = (
        f" The said deletion has caused acute hardship to the Appellant, who is "
        f"{intake.hardship}."
        if intake.hardship
        else ""
    )
    # (i) Natural justice.
    _numbered(
        doc,
        counter,
        "It is submitted that the impugned deletion was effected without the "
        "issuance of any prior notice or opportunity of being heard to the "
        "Appellant, in gross violation of the principles of natural justice "
        "(audi alteram partem)." + hardship_rider,
    )
    # (ii) Article 14 / right to vote / non-communication of the order.
    _numbered(
        doc,
        counter,
        "It is submitted that the impugned deletion is arbitrary and violative of "
        "Articles 14 and 21 of the Constitution of India, and defeats the "
        "Appellant's right to be enrolled and to vote under Article 326 thereof; "
        "further, no reasoned order has at any stage been communicated to the "
        "Appellant, depriving the Appellant of an effective opportunity to "
        "challenge the same.",
    )
    # (iii) Non-application of mind.
    _numbered(
        doc,
        counter,
        "It is submitted that the impugned deletion was carried out without any "
        "speaking order or justifiable cause and suffers from a manifest "
        "non-application of mind, the Appellant having been disenfranchised "
        "notwithstanding the prior submission of conclusive proofs of eligibility.",
    )
    # (iv) Incorrectly excluded despite sufficient documents.
    _numbered(
        doc,
        counter,
        "It is submitted that the Appellant was incorrectly excluded from the "
        "electoral roll notwithstanding that sufficient documents establishing "
        "the Appellant's identity, citizenship and ordinary residence were placed "
        "on record and accepted without objection.",
    )
    # Triggered: one ground however many names differ, to hold counsel's cap.
    if intake.mismatch_appellant_name or intake.mismatch_father_name:
        _numbered(
            doc,
            counter,
            "It is submitted that the variation relied upon is a mere clerical "
            "variation in the spelling of a name, occasioned in the preparation "
            "of the electoral roll and not attributable to the Appellant. Such a "
            "variation is no disqualification under the Representation of the "
            "People Act, 1950, and cannot sustain the deletion of the Appellant's "
            "name, the Appellant's identity being otherwise established by the "
            "documents produced.",
        )


def _submissions(doc: Document, intake: PetitionInput, counter: _Counter) -> None:
    """The elaboration, after the grounds — counsel: "then go into submissions".

    Where a ground states the violation, a submission argues this appellant's
    case on the facts. Nothing here restates a fact verbatim: counsel's markup
    asks that nothing be repeated.
    """
    _p(doc, "SUBMISSIONS", "heading")
    district = intake.district or "West Bengal"
    since = (
        f" since {intake.continuous_resident_since},"
        if intake.continuous_resident_since
        else ","
    )
    _numbered(
        doc,
        counter,
        f"It is submitted that the Appellant is a bona fide Indian citizen and a "
        f"continuous resident of {district}{since} holding multiple "
        f"government-issued documents of identity which have been verified by "
        f"competent authorities.",
        deep=True,
    )
    if intake.on_draft_roll:
        date = intake.draft_roll_date or "____"
        _numbered(
            doc,
            counter,
            f"It is submitted that the Appellant was duly included in the draft "
            f"roll published on {date}, having submitted all necessary details.",
            deep=True,
        )
    if intake.notice_received:
        _numbered(
            doc,
            counter,
            "It is submitted that the notice issued pursuant to a purported "
            "discrepancy is arbitrary, the reasons cited being non-est and "
            "comprising minor spelling variations and age mismatches, without any "
            "application of mind by the authority issuing the same.",
            deep=True,
        )
    if intake.hearing_attended:
        officer = intake.hearing_officer or "the hearing officer"
        _numbered(
            doc,
            counter,
            f"It is submitted that the Appellant submitted all necessary documents "
            f"at the time of the hearing before {officer}, to their satisfaction.",
            deep=True,
        )
    _numbered(
        doc,
        counter,
        "It is submitted that notwithstanding such bona fide conduct the "
        "Appellant's name has been included neither in the final electoral roll "
        "nor in the supplementary rolls.",
        deep=True,
    )
    # Triggered: mapped in the 2002 SIR and holding Aadhaar -> Motab Shaikh / ADR.
    if intake.mapped_2002_sir and intake.has_aadhaar:
        _numbered(
            doc,
            counter,
            "It is submitted that the judgments in W.P. (Civil) No. 399 of 2026 "
            "(Motab Shaikh v. Election Commission of India) and W.P. (Civil) No. "
            "640 of 2025 (Association for Democratic Reforms v. Election "
            "Commission of India) are squarely applicable to the Appellant herein, "
            "the Appellant's name having been mapped in the 2002 SIR and the "
            "Appellant holding an Aadhaar.",
            deep=True,
        )


def _prayer(doc: Document, intake: PetitionInput) -> None:
    _p(
        doc,
        "In the circumstances as aforesaid, your Petitioner most humbly prays "
        "that this Hon'ble Appellate Tribunal may graciously be pleased to:",
        left_indent=_RIGHT_COLUMN,
    )
    reliefs: list[str] = []
    if intake.relief_set_aside:
        reliefs.append(
            f"Set aside and/or quash the impugned order/action/decision of "
            f"deletion of the Appellant's name from the Supplementary Electoral "
            f"List dated {intake.deletion_date or '____'};"
        )
    if intake.relief_restore:
        ac_no = intake.constituency_no or "____"
        ac_name = intake.constituency_name or "____"
        part = intake.part_or_serial_no or "____"
        reliefs.append(
            f"Direct the respondents to forthwith restore the name of the "
            f"Appellant in the electoral roll of Assembly Constituency No. "
            f"{ac_no} — {ac_name}, at Part No. / Serial No. {part};"
        )
    if intake.relief_interim_vote:
        reliefs.append(
            "Pass an interim order permitting the Appellant to vote in the "
            "ensuing election;"
        )
    # Cascade-prayer: compensation is available only where hardship is pleaded.
    if intake.relief_compensation and intake.hardship:
        reliefs.append(
            "Award compensation for the anguish, mental agony and suffering "
            "caused to the Appellant;"
        )
    # boilerplate-rules.md §6: residuary clause is always the final relief.
    reliefs.append(
        "Pass such further or other order(s) as Your Honour may deem fit and "
        "proper in the interest of justice."
    )
    for i, relief in enumerate(reliefs):
        letter = chr(ord("a") + i)
        _p(
            doc,
            f"({letter}) {relief}",
            left_indent=_RIGHT_COLUMN + _HANGING,
            first_line_indent=-_HANGING,
        )


def _closing_tag(doc: Document, counter: _Counter) -> None:
    """Settled petition ¶23 — the last numbered paragraph, before the prayer."""
    _numbered(
        doc, counter, "This application is made bona fide and for the ends of justice."
    )


def _declaration(doc: Document, intake: PetitionInput) -> None:
    _p(doc, "D E C L A R A T I O N", "heading")
    # First person by legal form, as the settled petition has it — the third
    # person used elsewhere would be wrong in a sworn declaration.
    _p(
        doc,
        f"That I, {intake.appellant_name}, declare that the information provided "
        f"in this memorandum is true and correct to the best of my knowledge and "
        f"belief and that nothing material has been concealed or suppressed.",
    )
    _p(
        doc,
        "That I am aware that making the above statement or declaration in "
        "relation to this application which is false and which I know or believe "
        "to be false or do not believe to be true, is punishable under Section 31 "
        "of the Representation of the People Act, 1950 with imprisonment for a "
        "term which may extend to one year or with fine or with both.",
    )


def _verification(doc: Document, intake: PetitionInput) -> None:
    """Section G reaches the page: the volunteer types these once, in the form."""
    place = intake.place or "____"
    date = intake.declaration_date or "____"
    _p(doc, f"Place: {place}\t\tSignature: ____________", "left")
    _p(doc, f"Date: {date}", "left")


def _enclosures(doc: Document, intake: PetitionInput) -> None:
    _p(doc, "ENCLOSURES:", "left", bold=True)
    docs = _held_documents(intake)
    for i, (label, number) in enumerate(docs, start=1):
        suffix = f" bearing No. {number}" if number else ""
        _p(doc, f"{i}. Copy of {label}{suffix}.", "left")
