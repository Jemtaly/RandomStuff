param (
    [Parameter(Mandatory = $true)][string]$Name
)
$Time = Get-Date -Format "yyyyMMddHHmmss"
$OutD = "captures\$Name"
$OutF = "$OutD\$Time.ts"
$SrcW = "https://chaturbate.com/$Name/"
New-Item -ItemType Directory -Force -Path $OutD | Out-Null
streamlink $SrcW best -o $OutF
