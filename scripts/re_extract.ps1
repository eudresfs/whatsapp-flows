#requires -Version 7
# Re-run the DMC extractor over the cached HTML files (no re-fetch).

$ErrorActionPreference = "Stop"

$baseOut = "C:\Users\eudre\dev\skills\whatsapp-flows\docs\guides"
$tempDir = "C:\Users\eudre\dev\skills\whatsapp-flows\docs\guides\_html"
$script  = "C:\Users\eudre\dev\skills\whatsapp-flows\scripts\extract_dmc.py"

$pages = @(
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/';                              Html = 'index.html';                          Out = 'index.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/implementingyourflowendpoint/'; Html = 'implementing-flow-endpoint.html';     Out = 'implementing-flow-endpoint.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/interactive-flow-messages/';    Html = 'interactive-flow-messages.html';      Out = 'interactive-flow-messages.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/flows-templates/';              Html = 'flows-templates.html';                Out = 'flows-templates.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow/';                 Html = 'sending-a-flow.html';                 Out = 'sending-a-flow.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/receiveflowresponse/';          Html = 'receive-flow-response.html';          Out = 'receive-flow-response.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/healthmonitoring/';             Html = 'health-monitoring.html';              Out = 'health-monitoring.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/bestpractices/';                Html = 'best-practices.html';                 Out = 'best-practices.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/testingdebugging/';             Html = 'testing-debugging.html';              Out = 'testing-debugging.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/examples/';                     Html = 'examples.html';                       Out = 'examples.md' }
    @{ Source = 'https://developers.facebook.com/docs/whatsapp/flows/guides/whatsapp-business-encryption';  Html = 'whatsapp-business-encryption.html';   Out = 'whatsapp-business-encryption.md' }
)

$results = @()
foreach ($p in $pages) {
    $htmlFile = Join-Path $tempDir $p.Html
    $mdFile   = Join-Path $baseOut $p.Out
    if (-not (Test-Path $htmlFile)) { Write-Host "MISSING html: $htmlFile" -ForegroundColor Red; continue }
    Write-Host ""
    Write-Host "=== $($p.Out) ===" -ForegroundColor Cyan
    & python $script $htmlFile $mdFile --url $p.Source 2>&1 | ForEach-Object { "  $_" }
    $mdSize = (Get-Item $mdFile).Length
    $results += [pscustomobject]@{ File = $p.Out; MdBytes = $mdSize }
}

Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Green
$results | Format-Table -AutoSize
$totalMd = ($results | Measure-Object -Property MdBytes -Sum).Sum
Write-Host "Total Markdown bytes: $totalMd"
