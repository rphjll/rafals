# rafals - fabrique le fichier .env a partir de .env.exemple, avec des mots de passe et des cles tires au hasard.
# Appele par installer.bat. Ne fait rien si .env existe deja (on ne remplace jamais les mots de passe d'une base existante).
$ErrorActionPreference = 'Stop'
$racine = Split-Path -Parent $PSScriptRoot
$cible = Join-Path $racine '.env'
$modele = Join-Path $racine '.env.exemple'
if (Test-Path $cible) { Write-Host '.env existe deja : on le garde.'; exit 0 }

$hasard = [System.Security.Cryptography.RandomNumberGenerator]::Create()
function Octets([int]$n) { $b = New-Object byte[] $n; $hasard.GetBytes($b); return ,$b }
function Hex([int]$n) { return (-join ((Octets $n) | ForEach-Object { $_.ToString('x2') })) }
function Base64Url([byte[]]$b) { return [Convert]::ToBase64String($b).TrimEnd('=').Replace('+', '-').Replace('/', '_') }

# Cles des notifications (courbe P-256) : publique = 04 + X + Y, privee = D, en base64 « url »
$ec = [System.Security.Cryptography.ECDsa]::Create([System.Security.Cryptography.ECCurve]::CreateFromFriendlyName('nistP256'))
$p = $ec.ExportParameters($true)
$publique = Base64Url ([byte[]](@(4) + $p.Q.X + $p.Q.Y))
$privee = Base64Url $p.D

$texte = Get-Content -Raw -Encoding UTF8 $modele
# Chaque marque recoit sa propre valeur (deux mots de passe differents, par exemple)
$texte = [regex]::Replace($texte, '__ALEATOIRE_MOT_DE_PASSE__', { param($m) Hex 16 })
$texte = [regex]::Replace($texte, '__ALEATOIRE_HEX_64__', { param($m) Hex 32 })
$texte = [regex]::Replace($texte, '__ALEATOIRE_JETON__', { param($m) [Convert]::ToBase64String((Octets 32)).TrimEnd('=') })
$texte = [regex]::Replace($texte, '__ALEATOIRE_CLE_GARAGE__', { param($m) 'GK' + (Hex 12) })
$texte = $texte.Replace('__CLE_VAPID_PUBLIQUE__', $publique).Replace('__CLE_VAPID_PRIVEE__', $privee)
$texte = $texte.Replace('# rafals - modele du fichier .env', '# rafals - reglages et mots de passe de CE PC (fabrique par installer.bat)')

# Sans « BOM » au debut : Docker lirait sinon un nom de reglage abime
[System.IO.File]::WriteAllText($cible, $texte, (New-Object System.Text.UTF8Encoding $false))
Write-Host '.env cree, avec des mots de passe tires au hasard.'
