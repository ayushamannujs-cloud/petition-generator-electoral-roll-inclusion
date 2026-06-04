import { useEffect, useState } from "react";
import {
  generatePetition,
  previewPetition,
  type PetitionInput,
  type Gender,
  type Relative,
} from "./api";
import "./App.css";

const INITIAL: PetitionInput = {
  appellant_name: "",
  guardian_name: "",
  gender: "female",
  address: "",
  epic_no: "",
  contact: "",
  district: "",
  constituency_name: "",
  constituency_no: "",
  part_or_serial_no: "",
  prior_notice_before_deletion: true,
  relatives_on_roll: [],
  relief_set_aside: true,
  relief_restore: true,
  relief_interim_vote: true,
  relief_compensation: false,
};

function App() {
  const [form, setForm] = useState<PetitionInput>(INITIAL);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState("");

  const set = <K extends keyof PetitionInput>(k: K, v: PetitionInput[K]) =>
    setForm((f) => ({ ...f, [k]: v }));

  // Live preview: re-render (debounced) whenever the intake changes.
  useEffect(() => {
    if (!form.appellant_name.trim()) {
      setPreview("");
      return;
    }
    const id = setTimeout(() => {
      previewPetition(form)
        .then(setPreview)
        .catch(() => setPreview(""));
    }, 350);
    return () => clearTimeout(id);
  }, [form]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await generatePetition(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  // --- small field primitives ------------------------------------------------
  const Text = (k: keyof PetitionInput, label: string, area = false) => (
    <label className="field" key={k}>
      <span>{label}</span>
      {area ? (
        <textarea
          rows={3}
          value={(form[k] as string) ?? ""}
          onChange={(e) => set(k, e.target.value as never)}
        />
      ) : (
        <input
          type="text"
          value={(form[k] as string) ?? ""}
          onChange={(e) => set(k, e.target.value as never)}
        />
      )}
    </label>
  );

  const Check = (k: keyof PetitionInput, label: string) => (
    <label className="check" key={k}>
      <input
        type="checkbox"
        checked={Boolean(form[k])}
        onChange={(e) => set(k, e.target.checked as never)}
      />
      <span>{label}</span>
    </label>
  );

  // --- relatives repeater ----------------------------------------------------
  const relatives = form.relatives_on_roll ?? [];
  const setRelative = (i: number, patch: Partial<Relative>) =>
    set(
      "relatives_on_roll",
      relatives.map((r, j) => (j === i ? { ...r, ...patch } : r)),
    );
  const addRelative = () =>
    set("relatives_on_roll", [...relatives, { name: "", relationship: "", epic_no: "" }]);
  const removeRelative = (i: number) =>
    set("relatives_on_roll", relatives.filter((_, j) => j !== i));

  return (
    <main className="page">
      <header>
        <h1>SIR-2026 Electoral Roll Appeal</h1>
        <p className="subtitle">
          Re-inclusion petition generator. Fill the intake and download a
          formatted <code>.docx</code>. Only a handful of answers are
          load-bearing — the rest is data capture.
        </p>
      </header>

      <div className="layout">
      <form onSubmit={onSubmit}>
        <fieldset>
          <legend>A · Who you are</legend>
          {Text("appellant_name", "Full name (as on EPIC) *")}
          {Text("guardian_name", "Father's / Husband's name")}
          {Text("address", "Full residential address (with PIN)", true)}
          {Text("epic_no", "EPIC No.")}
          {Text("contact", "Mobile / email")}
          <label className="field">
            <span>Gender (drives every pronoun)</span>
            <select
              value={form.gender}
              onChange={(e) => set("gender", e.target.value as Gender)}
            >
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </label>
        </fieldset>

        <fieldset>
          <legend>B · Forum &amp; roll location</legend>
          {Text("district", "District")}
          {Text("constituency_name", "Assembly Constituency name")}
          {Text("constituency_no", "Constituency No.")}
          {Text("part_or_serial_no", "Part No. / Serial No.")}
        </fieldset>

        <fieldset>
          <legend>C · Your story (narrative beats)</legend>
          <p className="hint">Each toggle adds one chronological fact.</p>

          {Check("on_draft_roll", "Name in the Draft Roll (enumeration form submitted)")}
          {form.on_draft_roll && Text("draft_roll_date", "Draft-roll date")}

          {Check("notice_received", "Received a discrepancy / hearing notice")}
          {form.notice_received && (
            <>
              {Text("notice_no", "Notice No.")}
              {Text("notice_date", "Notice date")}
              {Text("notice_reason", "Reason stated in notice")}
            </>
          )}

          {Check("hearing_attended", "Attended the hearing + submitted documents")}
          {form.hearing_attended && (
            <>
              {Text("hearing_officer", "Officer (AERO)")}
              {Text("hearing_date", "Hearing date")}
            </>
          )}

          {Check("under_adjudication", "Final Roll marked 'Under Adjudication'")}
          {form.under_adjudication && Text("final_roll_date", "Final-roll date")}

          {Check("deleted", "Deleted via a Supplementary / Deleted-Electors list")}
          {form.deleted && (
            <>
              {Text("deletion_date", "Deletion date (impugned order)")}
              {Check("prior_notice_before_deletion", "Given notice/hearing before deletion")}
            </>
          )}

          {Check("appeal_filed", "Already filed the online appeal")}
          {form.appeal_filed && (
            <>
              {Text("appeal_no", "Appeal No.")}
              {Text("appeal_date", "Appeal date (≤15 days after deletion)")}
            </>
          )}
        </fieldset>

        <fieldset>
          <legend>D · Documents you hold</legend>
          {Check("has_voter_id", "Voter ID / EPIC")}
          {Check("has_aadhaar", "Aadhaar ⭐")}
          {form.has_aadhaar && Text("aadhaar_no", "Aadhaar No.")}
          {Check("has_passport", "Passport ⭐ (unlocks Passports Act 1967)")}
          {form.has_passport && Text("passport_no", "Passport No.")}
          {Check("has_pan", "PAN")}
          {Check("has_gst", "GST registration")}
          <label className="field">
            <span>Other documents (comma-separated)</span>
            <input
              type="text"
              placeholder="Ration card, Birth certificate"
              value={(form.other_documents ?? []).join(", ")}
              onChange={(e) =>
                set(
                  "other_documents",
                  e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean),
                )
              }
            />
          </label>
        </fieldset>

        <fieldset>
          <legend>E · Special legal triggers</legend>
          {Check("mapped_2002_sir", "Name mapped in the 2002/2003 SIR ⭐ (with Aadhaar → Motab Shaikh / ADR)")}
          {Text("continuous_resident_since", "Continuous resident since (year)")}

          <div className="repeater">
            <div className="repeater-head">
              <span>Close relatives currently on the roll</span>
              <button type="button" onClick={addRelative}>
                + Add relative
              </button>
            </div>
            {relatives.map((r, i) => (
              <div className="relative-row" key={i}>
                <input
                  placeholder="Name"
                  value={r.name}
                  onChange={(e) => setRelative(i, { name: e.target.value })}
                />
                <input
                  placeholder="Relationship"
                  value={r.relationship}
                  onChange={(e) => setRelative(i, { relationship: e.target.value })}
                />
                <input
                  placeholder="EPIC No."
                  value={r.epic_no ?? ""}
                  onChange={(e) => setRelative(i, { epic_no: e.target.value })}
                />
                <button type="button" className="remove" onClick={() => removeRelative(i)}>
                  ✕
                </button>
              </div>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>F · Hardship &amp; relief</legend>
          {Text("hardship", "Personal hardship (age, illness, caregiving) — describe", true)}
          {Check("relief_set_aside", "Set aside the deletion")}
          {Check("relief_restore", "Restore my name on the roll")}
          {Check("relief_interim_vote", "Interim order to vote in the upcoming election")}
          {Check("relief_compensation", "Compensation for mental agony (requires hardship)")}
        </fieldset>

        <fieldset>
          <legend>G · Declaration</legend>
          {Text("place", "Place")}
          {Text("declaration_date", "Date")}
        </fieldset>

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={busy || !form.appellant_name.trim()}>
          {busy ? "Generating…" : "Generate petition (.docx)"}
        </button>
      </form>

      <aside className="preview-pane">
        <div className="preview-head">Live preview</div>
        {preview ? (
          <div
            className="preview-doc"
            dangerouslySetInnerHTML={{ __html: preview }}
          />
        ) : (
          <p className="preview-empty">
            Enter the appellant's name to see the petition render here.
          </p>
        )}
      </aside>
      </div>
    </main>
  );
}

export default App;
