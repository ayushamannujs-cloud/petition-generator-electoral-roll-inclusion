export type Gender = "male" | "female" | "other";

export interface Relative {
  name: string;
  relationship: string;
  epic_no?: string;
}

export interface PetitionInput {
  // A — who you are
  appellant_name: string;
  guardian_name?: string;
  gender: Gender;
  address?: string;
  epic_no?: string;
  contact?: string;
  // B — forum & roll location
  district?: string;
  constituency_name?: string;
  constituency_no?: string;
  part_or_serial_no?: string;
  // C — narrative beats
  on_draft_roll?: boolean;
  draft_roll_date?: string;
  notice_received?: boolean;
  notice_no?: string;
  notice_date?: string;
  notice_reason?: string;
  hearing_attended?: boolean;
  hearing_officer?: string;
  hearing_date?: string;
  under_adjudication?: boolean;
  final_roll_date?: string;
  deleted?: boolean;
  deletion_date?: string;
  prior_notice_before_deletion?: boolean;
  appeal_filed?: boolean;
  appeal_no?: string;
  appeal_date?: string;
  // D — documents
  has_voter_id?: boolean;
  has_aadhaar?: boolean;
  aadhaar_no?: string;
  has_passport?: boolean;
  passport_no?: string;
  has_pan?: boolean;
  has_gst?: boolean;
  other_documents?: string[];
  // E — triggers
  mapped_2002_sir?: boolean;
  relatives_on_roll?: Relative[];
  continuous_resident_since?: string;
  // F — hardship & relief
  hardship?: string;
  relief_set_aside?: boolean;
  relief_restore?: boolean;
  relief_interim_vote?: boolean;
  relief_compensation?: boolean;
  // G — declaration
  place?: string;
  declaration_date?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

/** Returns an HTML preview of the petition (same content as the .docx). */
export async function previewPetition(input: PetitionInput): Promise<string> {
  const resp = await fetch(`${API_BASE}/api/petition/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!resp.ok) {
    if (resp.status === 422) return ""; // incomplete/invalid intake — no preview yet
    throw new Error(`Preview failed (${resp.status})`);
  }
  return resp.text();
}

/** Posts the intake and triggers a browser download of the generated .docx. */
export async function generatePetition(input: PetitionInput): Promise<void> {
  const resp = await fetch(`${API_BASE}/api/petition`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(`Generation failed (${resp.status}): ${detail}`);
  }

  const blob = await resp.blob();
  const disposition = resp.headers.get("content-disposition") ?? "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match?.[1] ?? "petition.docx";

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
