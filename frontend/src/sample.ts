import type { PetitionInput } from "./api";

// A fictitious appellant for the "Fill sample case" demo. Every name, number
// and address here is invented — never paste a real case file in.
// It ticks the load-bearing triggers (marriage move, name variation, Aadhaar +
// 2002 mapping, passport, hardship → compensation) so one click shows how far
// the petition adapts.
export const SAMPLE: PetitionInput = {
  appellant_name: "Rehana Khatun",
  guardian_name: "Abdul Karim Sheikh",
  spouse_name: "Imran Hossain",
  gender: "female",
  address: "14/2 Sample Lane, Park Circus, Kolkata – 700017",
  epic_no: "XYZ0000000",
  contact: "",
  tribunal_venue: "Entally Jessop Building, Kolkata",
  district: "Kolkata South",
  constituency_name: "Ballygunge",
  constituency_no: "161",
  part_or_serial_no: "Part 112 / Serial 487",

  on_draft_roll: true,
  draft_roll_date: "16.12.2025",
  notice_received: true,
  notice_no: "SIR/161/2026/0000",
  notice_date: "05.01.2026",
  notice_reason: "Logical discrepancy: father's name does not match the 2002 roll",
  hearing_attended: true,
  hearing_officer: "AERO, 161-Ballygunge AC",
  hearing_date: "19.01.2026",
  under_adjudication: true,
  final_roll_date: "14.02.2026",
  deleted: true,
  deletion_date: "02.03.2026",
  prior_notice_before_deletion: false,
  appeal_filed: true,
  appeal_no: "APL/2026/000000",
  appeal_date: "12.03.2026",

  mismatch_appellant_name: true,
  name_on_roll: "Rehana Khatoon",
  mismatch_father_name: true,
  father_name_on_roll: "Abdul Karim Sk.",
  address_changed: true,
  address_change_reason: "marriage",
  previous_address: "Village Sample, P.O. Domkal, Murshidabad",
  previous_constituency: "Domkal",
  registered_since: "2004",
  marriage_date: "11.02.2015",

  has_voter_id: true,
  has_aadhaar: true,
  aadhaar_no: "XXXX XXXX 0000",
  has_passport: true,
  passport_no: "X0000000",
  has_pan: true,
  has_gst: false,
  other_documents: ["Ration card", "Marriage certificate"],

  mapped_2002_sir: true,
  continuous_resident_since: "2015",
  relatives_on_roll: [
    { name: "Imran Hossain", relationship: "Husband", epic_no: "XYZ0000001" },
    { name: "Abdul Karim Sheikh", relationship: "Father", epic_no: "XYZ0000002" },
  ],

  hardship:
    "The Appellant is the sole caregiver of her mother-in-law, who is bedridden, and the deletion has caused her severe mental agony",
  relief_set_aside: true,
  relief_restore: true,
  relief_interim_vote: true,
  relief_compensation: true,

  place: "Kolkata",
  declaration_date: "16.03.2026",
};

// The 22 Eighth Schedule languages, in their own script. Only English is built;
// the rest are shown so the roadmap is visible.
export const LANGUAGES: { code: string; english: string; native: string }[] = [
  { code: "en", english: "English", native: "English" },
  { code: "as", english: "Assamese", native: "অসমীয়া" },
  { code: "bn", english: "Bengali", native: "বাংলা" },
  { code: "brx", english: "Bodo", native: "बड़ो" },
  { code: "doi", english: "Dogri", native: "डोगरी" },
  { code: "gu", english: "Gujarati", native: "ગુજરાતી" },
  { code: "hi", english: "Hindi", native: "हिन्दी" },
  { code: "kn", english: "Kannada", native: "ಕನ್ನಡ" },
  { code: "ks", english: "Kashmiri", native: "كٲشُر" },
  { code: "kok", english: "Konkani", native: "कोंकणी" },
  { code: "mai", english: "Maithili", native: "मैथिली" },
  { code: "ml", english: "Malayalam", native: "മലയാളം" },
  { code: "mni", english: "Manipuri", native: "মৈতৈলোন্" },
  { code: "mr", english: "Marathi", native: "मराठी" },
  { code: "ne", english: "Nepali", native: "नेपाली" },
  { code: "or", english: "Odia", native: "ଓଡ଼ିଆ" },
  { code: "pa", english: "Punjabi", native: "ਪੰਜਾਬੀ" },
  { code: "sa", english: "Sanskrit", native: "संस्कृतम्" },
  { code: "sat", english: "Santali", native: "ᱥᱟᱱᱛᱟᱲᱤ" },
  { code: "sd", english: "Sindhi", native: "سنڌي" },
  { code: "ta", english: "Tamil", native: "தமிழ்" },
  { code: "te", english: "Telugu", native: "తెలుగు" },
  { code: "ur", english: "Urdu", native: "اردو" },
];
