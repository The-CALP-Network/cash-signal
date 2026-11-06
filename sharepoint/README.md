# Regional representative notes: SharePoint list → dashboard

Regional reps edit one row per country in a SharePoint list. An hourly Power Automate flow
turns the list into `data/rep/rep_notes.json` and commits it to this repo through the GitHub
API (premium HTTP action, no new connector, no app registration). A GitHub Action rebuilds
`index.html` on that push. Reps see their edits on the dashboard within about an hour.

```
SharePoint list  ──(flow, hourly, only when changed)──►  data/rep/rep_notes.json  ──(Action)──►  index.html
```

The researched layer (`data/<country>.json`, FTS pulls, CWG pulls) is never touched by the
list; `build/build.py` overlays the rep notes at build time. If the flow stops, the dashboard
keeps the last export.

## 1. The list

Run `New-RepNotesList.ps1` once against the site you want it on (needs PnP.PowerShell and
your own login). It creates the list, the columns and 15 seeded rows.

| Column (internal name) | Type | Feeds |
|---|---|---|
| Title | text (built in) | country name, display only |
| Country ID (`CountryID`) | text | **join key** = `id` in `data/<country>.json`; do not edit |
| Key messages (`KeyMessages`) | multi-line, plain text | `rep_notes.key_messages` |
| Barriers (`Barriers`) | multi-line, plain text | `rep_notes.barriers` |
| CWG maturity (`CWGMaturity`) | choice: Nascent / Developing / Functioning / Strong / Unknown | `rep_notes.cwg_maturity` |
| Leadership buy-in (`LeadershipBuyIn`) | choice: Low / Medium / High / Unknown | `rep_notes.leadership_buy_in` |
| CALP priority (`CALPPriority`) | choice: High / Medium / Low / Watch | `rep_notes.calp_priority` |
| Reviewed by (`ReviewedBy`) | person | `rep_notes.reviewed_by` (display name); setting it flips the country to "Reviewed" |
| Reviewed date (`ReviewedDate`) | date | `rep_notes.reviewed_date`; if empty the row's Modified date is used |
| Region (`Region`) | text | grouping in the list view only |

Afterwards, in the list settings:
- Versioning is on (the script sets it): that is the audit trail.
- Permissions: give the reps group Edit. Advanced settings → "Create and Edit access: Create items and edit items that were created by the user" does not fit (rows are seeded by you), so rely on the fact that the dashboard ignores added rows (no matching `CountryId`) and deleted rows simply fall back to blank notes. Turn off attachments (script does) and consider hiding the Country id column from the form.
- Group the default view by Region, show Modified and Modified By.

Paste the list URL into `REP_LIST_URL` at the top of the data script in `build/template.html`;
each country page then links "Edit in the SharePoint list".

## 2. The flow

See `flow.md` for the step-by-step with the exact expressions. In short:

1. **Recurrence**, every hour.
2. **Get items** (SharePoint) from the list, 100 rows.
3. **Select** rows → the JSON shape below.
4. **Compose** the file text.
5. **HTTP GET** the current file from GitHub (for the blob SHA and to compare).
6. **Condition**: unchanged → terminate; changed → **HTTP PUT** the new content.

Output shape (`data/rep/rep_notes.json`), one object per row:

```json
[{"id":"sudan","country":"Sudan","key_messages":"...","barriers":"...","cwg_maturity":"Functioning",
  "leadership_buy_in":"Medium","calp_priority":"High","reviewed_by":"Jane Doe",
  "reviewed_date":"2026-11-06","modified":"2026-11-06T14:02:11Z","editor":"Jane Doe"}]
```

## 3. GitHub

- `.github/workflows/build.yml` validates, rebuilds and commits `index.html` on any push that
  touches `data/`, `build/` or `schema/`. Pages keeps serving from `main`.
- Create a **fine-grained personal access token**: GitHub → Settings → Developer settings →
  Fine-grained tokens → repository access: only `The-CALP-Network/cash-signal` → permissions:
  Contents **Read and write**. Expiry max 1 year: put the renewal date in your calendar now,
  because an expired token fails silently inside the flow (step 7 in `flow.md` adds an alert).
- Because the Action commits `index.html` back to `main`, **pull before you work in VS Code**.
  `git pull --rebase` before each editing session is enough.

## Things that can bite

- **DLP**: if the tenant's data loss prevention policy keeps SharePoint and HTTP in different
  groups, the flow is blocked at save time with an explicit message. Then it is an IT ticket.
- **Rich text**: the script sets the two note columns to plain text. If someone switches them
  to rich text, HTML arrives in the dashboard. `build.py` does not strip tags.
- **Person column**: the flow sends the display name only, never the email.
- **Duplicate CountryId**: last row wins. The list has no uniqueness constraint; you can add one
  (column settings → Enforce unique values) after seeding.
