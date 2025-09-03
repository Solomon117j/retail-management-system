# PowerShell script to generate self-signed SSL certificates for development

$certPath = ".\certs"
$certFile = "devserver.crt"
$keyFile = "devserver.key"

# Create certs directory if it doesn't exist
if (-Not (Test-Path $certPath)) {
    New-Item -ItemType Directory -Path $certPath
}

# Generate self-signed certificate
Write-Host "Generating self-signed SSL certificate for development..."

$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My" -NotAfter (Get-Date).AddYears(1)

# Export the certificate and private key
$pfxPath = Join-Path $certPath "devserver.pfx"
$certPassword = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $certPassword

# Export the certificate (crt)
$certExportPath = Join-Path $certPath $certFile
Export-Certificate -Cert $cert -FilePath $certExportPath

# Export the private key (key)
$keyExportPath = Join-Path $certPath $keyFile
# Extract private key using OpenSSL (requires OpenSSL installed and in PATH)
Write-Host "Extracting private key using OpenSSL..."
openssl pkcs12 -in $pfxPath -nocerts -nodes -password pass:password -out $keyExportPath

Write-Host "Certificate and key generated at $certPath"
