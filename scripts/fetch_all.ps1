#requires -Version 7
# Fetch all WhatsApp Flows guide pages and convert them to Markdown.
#
# - Always uses `?locale=en_US` to force English content.
# - Strips trailing slash from the path (FB returns HTTP 400 with it).
# - Saves raw HTML to a temp folder, then runs the DMC->Markdown extractor.

$ErrorActionPreference = "Stop"

$baseOut = "C:\Users\eudre\dev\skills\whatsapp-flows\docs\guides"
$tempDir = "C:\Users\eudre\dev\skills\whatsapp-flows\docs\guides\_html"
$script  = "C:\Users\eudre\dev\skills\whatsapp-flows\scripts\extract_dmc.py"

if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir | Out-Null }

# Manifest: original (canonical short) URL recorded for the Source: line,
# and the actual fetch URL (the slashless form against `/docs/...` or the
# `/documentation/business-messaging/...` long form for slugs that only
# resolve there).
$pages = @(
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/';                              Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides';                                                                   Out = 'index.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/implementingyourflowendpoint/'; Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides/implementingyourflowendpoint';                                       Out = 'implementing-flow-endpoint.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/interactive-flow-messages/';    Fetch = 'https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/interactive-flow-messages';            Out = 'interactive-flow-messages.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/flows-templates/';              Fetch = 'https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/flows-templates';                      Out = 'flows-templates.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow/';                 Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow';                                                      Out = 'sending-a-flow.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/receiveflowresponse/';          Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides/receiveflowresponse';                                                Out = 'receive-flow-response.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/healthmonitoring/';             Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides/healthmonitoring';                                                  Out = 'health-monitoring.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/bestpractices/';                Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides/bestpractices';                                                     Out = 'best-practices.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/testingdebugging/';             Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides/testingdebugging';                                                  Out = 'testing-debugging.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/examples/';                     Fetch = 'https://developers.facebook.com/docs/whatsapp/flows/guides/examples';                                                          Out = 'examples.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/whatsapp-business-encryption';  Fetch = 'https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/whatsapp-business-encryption';         Out = 'whatsapp-business-encryption.md' }
)

# Empirically the short UA passes the WAF when the full Chrome UA does not.
$ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

function Fetch-Page {
    param([string]$Url, [string]$OutFile, [string]$UserAgent)
    # Mirror the manual call that empirically works: short UA, only
    # Accept-Language, no extra Accept header, single-line invocation.
    return (curl.exe -sSL -A $UserAgent -H "Accept-Language: en-US,en;q=0.9" -o $OutFile -w "%{http_code}" $Url)
}

$results = @()
$first = $true
$failures = @()
foreach ($p in $pages) {
    if (-not $first) { Start-Sleep -Seconds 8 }
    $first = $false

    $sourceUrl = $p.Source
    $fetchUrl  = $p.Fetch
    $htmlFile  = Join-Path $tempDir ($p.Out -replace '\.md$', '.html')
    $mdFile    = Join-Path $baseOut  $p.Out

    Write-Host ""
    Write-Host "=== $($p.Out) ===" -ForegroundColor Cyan
    Write-Host "fetch: $fetchUrl"

    $status = Fetch-Page -Url $fetchUrl -OutFile $htmlFile -UserAgent $ua
    $htmlSize = (Get-Item $htmlFile).Length
    Write-Host "  HTTP $status, $htmlSize bytes"

    if ($status -ne "200") {
        Write-Host "  ! non-200; will retry in final pass" -ForegroundColor Yellow
        $results += [pscustomobject]@{ File = $p.Out; HtmlBytes = $htmlSize; MdBytes = 0; Status = "HTTP $status (pending retry)" }
        $failures += $p
        Start-Sleep -Seconds 60  # cool down after a rejection
        continue
    }

    # Extract.
    try {
        & python $script $htmlFile $mdFile --url $sourceUrl 2>&1 | ForEach-Object { "  $_" }
        $mdSize = (Get-Item $mdFile).Length
        Write-Host "  -> $mdFile ($mdSize bytes)"
        $results += [pscustomobject]@{ File = $p.Out; HtmlBytes = $htmlSize; MdBytes = $mdSize; Status = "OK" }
    } catch {
        Write-Host "  EXTRACT FAILED: $_" -ForegroundColor Red
        $results += [pscustomobject]@{ File = $p.Out; HtmlBytes = $htmlSize; MdBytes = 0; Status = "EXTRACT FAILED: $_" }
    }
}

if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "=== RETRY PASS ($($failures.Count) pages) ===" -ForegroundColor Magenta
    Write-Host "Waiting 120s before retry pass to clear any WAF state..."
    Start-Sleep -Seconds 120
    foreach ($p in $failures) {
        Start-Sleep -Seconds 15  # extra pacing in retry pass
        $sourceUrl = $p.Source
        $fetchUrl  = $p.Fetch
        $htmlFile  = Join-Path $tempDir ($p.Out -replace '\.md$', '.html')
        $mdFile    = Join-Path $baseOut  $p.Out
        Write-Host ""
        Write-Host "RETRY: $($p.Out)" -ForegroundColor Cyan
        $status = Fetch-Page -Url $fetchUrl -OutFile $htmlFile -UserAgent $ua
        $htmlSize = (Get-Item $htmlFile).Length
        Write-Host "  HTTP $status, $htmlSize bytes"
        if ($status -eq "200") {
            try {
                & python $script $htmlFile $mdFile --url $sourceUrl 2>&1 | ForEach-Object { "  $_" }
                $mdSize = (Get-Item $mdFile).Length
                Write-Host "  -> $mdFile ($mdSize bytes)"
                # Update results row
                $row = $results | Where-Object { $_.File -eq $p.Out } | Select-Object -First 1
                if ($row) {
                    $row.HtmlBytes = $htmlSize
                    $row.MdBytes   = $mdSize
                    $row.Status    = "OK (retry)"
                }
            } catch {
                Write-Host "  EXTRACT FAILED: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  ! still non-200" -ForegroundColor Yellow
            $row = $results | Where-Object { $_.File -eq $p.Out } | Select-Object -First 1
            if ($row) { $row.Status = "HTTP $status (retry failed)" }
        }
    }
}

Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Green
$results | Format-Table -AutoSize
$totalMd = ($results | Measure-Object -Property MdBytes -Sum).Sum
Write-Host "Total Markdown bytes: $totalMd"
