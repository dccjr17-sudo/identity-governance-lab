# Run from any folder. Prefer installed Python; otherwise use Codex's bundled runtime.
$ErrorActionPreference = 'Stop'
$bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython (Join-Path $PSScriptRoot 'import_hr.py')
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 (Join-Path $PSScriptRoot 'import_hr.py')
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python (Join-Path $PSScriptRoot 'import_hr.py')
} else {
    throw 'Python 3 is required to run the HR import.'
}
if ($LASTEXITCODE -ne 0) { throw 'HR import failed. Review the error above.' }
