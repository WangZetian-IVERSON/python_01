# PowerShell wrapper to download ResNet50 pretrained weights
param(
    [string]$OutDir = "initmodel",
    [switch]$Force
)

$python = "python"
$script = Join-Path $PSScriptRoot "download_resnet50.py"
if(-not (Test-Path $script)){
    Write-Error "download_resnet50.py not found in $PSScriptRoot"
    exit 1
}

$args = "--out-dir `"$OutDir`""
if($Force){ $args += ' --force' }

& $python $script $args
