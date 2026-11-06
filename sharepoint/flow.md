# Power Automate flow: "Cash Signal Updates → GitHub"

Build this as a scheduled cloud flow in the environment where you have the premium licence.
Every step below is a standard action; the only premium one is HTTP.

## 0. Settings

- Flow name: `Cash Signal Updates → GitHub`
- Run-only user: you. The SharePoint connection is yours; the token is yours.
- Flow settings → Concurrency control → on, degree of parallelism **1** (so two runs never race on the SHA).

## 1. Trigger: Recurrence

Interval 1, frequency Hour. (Reps are asynchronous across time zones; hourly is plenty, and it
keeps rebuilds far under GitHub Pages' 10 per hour soft limit.) Add a `Manually trigger`
variant later if you want a "publish now" button.

## 2. SharePoint: Get items

- Site address: the site
- List name: `Cash Signal Updates`
- Top count: 100
- Leave the Select/Expand queries empty: 15 rows is nothing, and the connector then returns
  person and choice columns as full objects, which the expressions below expect.

## 3. Data Operation: Select

From: `body('Get_items')?['value']`

Map (switch to text mode and paste the right-hand expressions one at a time; every field uses
`coalesce(...,'')` so empty cells become `""` not `null`):

| key | value expression |
|---|---|
| id | `toLower(trim(coalesce(item()?['CountryID'],'')))` |
| country | `coalesce(item()?['Title'],'')` |
| key_messages | `coalesce(item()?['KeyMessages'],'')` |
| barriers | `coalesce(item()?['Barriers'],'')` |
| cwg_maturity | `coalesce(item()?['CWGMaturity']?['Value'],'')` |
| leadership_buy_in | `coalesce(item()?['LeadershipBuyIn']?['Value'],'')` |
| calp_priority | `coalesce(item()?['CALPPriority']?['Value'],'')` |
| reviewed_by | `coalesce(item()?['ReviewedBy']?['DisplayName'],'')` |
| reviewed_date | `if(empty(item()?['ReviewedDate']),'',formatDateTime(item()?['ReviewedDate'],'yyyy-MM-dd'))` |
| modified | `item()?['Modified']` |
| editor | `coalesce(item()?['Editor']?['DisplayName'],'')` |

Note: choice columns come back as objects (`{Value: "High"}`) and person columns as objects with
`DisplayName`; the expressions above unwrap them. If a column name was created differently,
the internal name is what matters: check it in the column's URL (`Field=...`).

## 4. Data Operation: Compose — "FileText"

Inputs (expression): `string(body('Select'))`

This is the exact text that will be committed. Sorting is not needed: Get items returns rows
in ID order, which is stable.

## 5. HTTP — "GetCurrent"

- Method: GET
- URI: `https://api.github.com/repos/The-CALP-Network/cash-signal/contents/data/rep/rep_notes.json?ref=main`
- Headers:
  - `Authorization`: `Bearer <token>`  (better: keep the token in an environment variable or Azure Key Vault secret, and reference it here)
  - `Accept`: `application/vnd.github+json`
  - `User-Agent`: `cash-signal-flow`
- Settings → Configure run after: nothing special. If the file does not exist yet, this returns
  404; handle that in step 6 by treating the SHA as empty.

## 6. Condition — "Changed?"

Expression (advanced mode):

```
not(equals(
  base64ToString(replace(coalesce(body('GetCurrent')?['content'],''), decodeUriComponent('%0A'), '')),
  outputs('FileText')
))
```

GitHub returns `content` base64-encoded with newlines every 60 characters; the `replace`
removes them before decoding.

**If no**: Terminate (Succeeded). Nothing changed, nothing committed.

**If yes**: step 7.

## 7. HTTP — "PutFile" (inside the Yes branch)

- Method: PUT
- URI: `https://api.github.com/repos/The-CALP-Network/cash-signal/contents/data/rep/rep_notes.json`
- Headers: same three as step 5, plus `Content-Type`: `application/json`
- Body:

```json
{
  "message": "Rep notes from SharePoint, @{utcNow('yyyy-MM-dd HH:mm')} UTC",
  "branch": "main",
  "content": "@{base64(outputs('FileText'))}",
  "sha": "@{body('GetCurrent')?['sha']}"
}
```

`data/rep/rep_notes.json` is already committed (an empty array), so the GET always finds it
and `sha` is always set. (Creating a missing file would mean omitting the `sha` key.)

GitHub replies 200 (updated) or 201 (created). A 409 means someone pushed between the GET and
the PUT; the next hourly run resolves it. A 401 means the token has expired.

## 8. Alert on failure (recommended)

Add a parallel branch after step 7 → **Office 365 Outlook: Send an email (V2)** to yourself,
Configure run after → **has failed** / **has timed out** only. Subject:
`Cash Signal flow failed: @{workflow()['run']['name']}` and the body
`@{result('PutFile')}`. This is the only way you learn the token expired.

## Testing

1. Save, then **Test → Manually** with the list unchanged. Expect the No branch (terminate).
2. Edit one cell in the list, run again. Expect 200 from PutFile, a new commit on `main`
   touching `data/rep/rep_notes.json`, and a "Rebuild dashboard" commit from the Action a minute
   later. Open the Pages URL: the country shows the note at the top of its tab.
3. Set *Reviewed by* on a row and leave the date blank: the country header should switch to
   "Reviewed by … , <Modified date>".

## Later

- Push-on-change instead of hourly: add a second flow with trigger *When an item is created or
  modified*, a 3-minute Delay, then the same steps 2–7. Keep concurrency at 1. Hourly is simpler.
- If IT blocks SharePoint + HTTP in one flow (DLP), the pull alternative is a GitHub Action
  reading the list through Graph with an app registration: that needs admin consent once.
