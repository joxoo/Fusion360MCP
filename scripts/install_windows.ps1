[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$SourceDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$AddinsRoot = (Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns"),
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SourceDir)) {
    throw "Source directory not found: $SourceDir"
}

if (-not $env:APPDATA) {
    throw "APPDATA is not set. This installer must run on Windows."
}

$addonName = "FusionMCP"
$targetDir = Join-Path $AddinsRoot $addonName
$stagingDir = Join-Path ([System.IO.Path]::GetTempPath()) ("FusionMCP_install_" + [System.Guid]::NewGuid().ToString("N"))

$excludeDirs = @(
    ".git",
    ".venv",
    ".vscode",
    "__pycache__",
    "tests",
    "tmp",
    "build",
    "dist"
)

$excludeFiles = @(
    ".DS_Store",
    "*.pyc",
    "*.pyo"
)

function Copy-FilteredTree {
    param(
        [Parameter(Mandatory = $true)][string]$From,
        [Parameter(Mandatory = $true)][string]$To
    )

    New-Item -ItemType Directory -Force -Path $To | Out-Null

    Get-ChildItem -LiteralPath $From -Force | ForEach-Object {
        if ($_.PSIsContainer) {
            if ($excludeDirs -contains $_.Name) {
                return
            }

            Copy-FilteredTree -From $_.FullName -To (Join-Path $To $_.Name)
            return
        }

        foreach ($pattern in $excludeFiles) {
            if ($_.Name -like $pattern) {
                return
            }
        }

        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $To $_.Name) -Force
    }
}

Write-Host "Source      : $SourceDir"
Write-Host "Target      : $targetDir"
Write-Host "Staging     : $stagingDir"

if ($PSCmdlet.ShouldProcess($targetDir, "Install FusionMCP into the Fusion 360 Add-Ins directory")) {
    New-Item -ItemType Directory -Force -Path $AddinsRoot | Out-Null
    New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null

    try {
        Copy-FilteredTree -From $SourceDir -To $stagingDir

        if (Test-Path $targetDir) {
            if ($Clean) {
                Remove-Item -LiteralPath $targetDir -Recurse -Force
            } else {
                Get-ChildItem -LiteralPath $targetDir -Force | Remove-Item -Recurse -Force
            }
        } else {
            New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        }

        Get-ChildItem -LiteralPath $stagingDir -Force | ForEach-Object {
            Move-Item -LiteralPath $_.FullName -Destination (Join-Path $targetDir $_.Name) -Force
        }

        $manifestPath = Join-Path $targetDir "FusionMCP.manifest"
        if (-not (Test-Path $manifestPath)) {
            throw "Installation failed: manifest missing at $manifestPath"
        }

        Write-Host ""
        Write-Host "FusionMCP was installed successfully."
        Write-Host "Add-In path : $targetDir"
        Write-Host ""
        Write-Host "Next steps:"
        Write-Host "1. Start Fusion 360."
        Write-Host "2. Open Utilities > Scripts and Add-Ins."
        Write-Host "3. Start the 'FusionMCP' add-in."
    }
    finally {
        if (Test-Path $stagingDir) {
            Remove-Item -LiteralPath $stagingDir -Recurse -Force
        }
    }
}
