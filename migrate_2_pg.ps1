# Create PostgreSQL database and user
# Run in PowerShell as Administrator if you want environment variables persisted for your user.

param(
  [string]$ProjectRoot = "c:\Users\Thembinkosi\Desktop\retail_management_system",
  [string]$DbName      = "retail_management",
  [string]$DbUser      = "thembinkosi",
  [string]$DbPass      = "Only4u@2025@#",
  [string]$DbHost      = "127.0.0.1",
  [string]$DbPort      = "5432",
  [string]$PgSuperUser = "postgres",
  [string]$PgSuperPass = "Only4u@12345"
)

$ErrorActionPreference = "Stop"

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Ok($m){ Write-Host "[OK]  $m" -ForegroundColor Green }

# 1) Create PostgreSQL database and user (requires psql)
Info "Checking for psql"
$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
  Warn "psql not found on PATH. Ensure PostgreSQL client tools are installed and psql is available, then rerun."
  throw "psql missing"
}

if (-not $PgSuperPass -or $PgSuperPass -eq "") {
  $PgSuperPass = Read-Host -AsSecureString "Enter PostgreSQL superuser password for user '$PgSuperUser'"
  $PgSuperPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($PgSuperPass)
  )
} else {
  $PgSuperPassPlain = $PgSuperPass
}

# Escape password for SQL
$escapedDbPass = $DbPass -replace "'", "''"

# Create DB and user
Info "Creating DB and user (if not already present)"
# $env:PGPASSWORD = $PgSuperPassPlain  # Not needed for trust

# Create user if not exists
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h $DbHost -p $DbPort -U $PgSuperUser -d postgres -c "
CREATE USER $DbUser WITH PASSWORD '$escapedDbPass';" 2>$null
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h $DbHost -p $DbPort -U $PgSuperUser -d postgres -c "
ALTER USER $DbUser WITH PASSWORD '$escapedDbPass';" 2>$null

# Create database if not exists
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h $DbHost -p $DbPort -U $PgSuperUser -d postgres -v ON_ERROR_STOP=1 -c "
CREATE DATABASE $DbName WITH OWNER $DbUser ENCODING 'UTF8';" 2>$null

# Grant privileges
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h $DbHost -p $DbPort -U $PgSuperUser -d postgres -v ON_ERROR_STOP=1 -c "
GRANT ALL PRIVILEGES ON DATABASE $DbName TO $DbUser;" | Out-Host

Ok "Database created successfully!"
