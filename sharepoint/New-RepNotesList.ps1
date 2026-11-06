# Creates the "Cash Signal rep notes" list on a SharePoint site and seeds one row per country.
# Run once, interactively, with your own CALP login (no app registration needed):
#   Install-Module PnP.PowerShell -Scope CurrentUser   # once
#   .\New-RepNotesList.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<site>
param(
  [Parameter(Mandatory)] [string] $SiteUrl,
  [string] $ListName = "Cash Signal rep notes"
)

Connect-PnPOnline -Url $SiteUrl -Interactive

$list = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue
if (-not $list) {
  $list = New-PnPList -Title $ListName -Template GenericList -EnableVersioning
  Write-Host "Created list $ListName"
}

# Title = country name (built in). CountryId must equal the id in data/<country>.json: that is the join key.
Add-PnPField -List $ListName -DisplayName "Country id"        -InternalName "CountryId"       -Type Text -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "Key messages"      -InternalName "KeyMessages"     -Type Note -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "Barriers"          -InternalName "Barriers"        -Type Note -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "CWG maturity"      -InternalName "CWGMaturity"     -Type Choice -Choices "Nascent","Developing","Functioning","Strong","Unknown" -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "Leadership buy-in" -InternalName "LeadershipBuyIn" -Type Choice -Choices "Low","Medium","High","Unknown" -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "CALP priority"     -InternalName "CalpPriority"    -Type Choice -Choices "High","Medium","Low","Watch" -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "Reviewed by"       -InternalName "ReviewedBy"      -Type User -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "Reviewed date"     -InternalName "ReviewedDate"    -Type DateTime -AddToDefaultView -ErrorAction SilentlyContinue
Add-PnPField -List $ListName -DisplayName "Region"            -InternalName "Region"          -Type Text -AddToDefaultView -ErrorAction SilentlyContinue

# plain text, not rich text, so the dashboard gets clean strings
foreach ($f in "KeyMessages","Barriers") { Set-PnPField -List $ListName -Identity $f -Values @{ RichText = $false } }

# One row per country, same ids as data/*.json
$countries = @(
  @{ id="afghanistan"; name="Afghanistan";       region="Asia-Pacific" },
  @{ id="chad";        name="Chad";              region="West and Central Africa" },
  @{ id="drc";         name="DRC";               region="West and Central Africa" },
  @{ id="lebanon";     name="Lebanon";           region="MENA" },
  @{ id="mali";        name="Mali";              region="West and Central Africa" },
  @{ id="mozambique";  name="Mozambique";        region="East and Southern Africa" },
  @{ id="myanmar";     name="Myanmar";           region="Asia-Pacific" },
  @{ id="niger";       name="Niger";             region="West and Central Africa" },
  @{ id="nigeria";     name="Nigeria";           region="West and Central Africa" },
  @{ id="opt";         name="Gaza (oPt)";        region="MENA" },
  @{ id="somalia";     name="Somalia";           region="East and Southern Africa" },
  @{ id="southsudan";  name="South Sudan";       region="East and Southern Africa" },
  @{ id="sudan";       name="Sudan";             region="East and Southern Africa" },
  @{ id="syria";       name="Syria";             region="MENA" },
  @{ id="yemen";       name="Yemen";             region="MENA" }
)
$existing = (Get-PnPListItem -List $ListName -Fields "CountryId").FieldValues.CountryId
foreach ($c in $countries) {
  if ($existing -contains $c.id) { continue }
  Add-PnPListItem -List $ListName -Values @{ Title=$c.name; CountryId=$c.id; Region=$c.region } | Out-Null
  Write-Host "Added $($c.name)"
}

# Reps edit their own rows; nobody adds or deletes rows (the country set is fixed in the repo).
Set-PnPList -Identity $ListName -EnableAttachments $false
Write-Host "Done. List URL: $SiteUrl/Lists/$($ListName -replace ' ','')"
