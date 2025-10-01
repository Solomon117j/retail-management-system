# TODO: Fix HTTP to HTTPS Redirection Issue

## Issue Description
When clicking the link `http://127.0.0.1:8000/`, it redirects to `https://127.0.0.1:8000/`, even when running the standard Django development server.

## Root Cause Analysis
- Browser has cached HSTS (HTTP Strict Transport Security) settings for localhost from previous HTTPS access
- HSTS forces browsers to automatically redirect HTTP requests to HTTPS for domains that have been accessed via HTTPS
- This persists even after stopping the HTTPS server

## Solution Implemented
- Updated `SYSTEM_DOCUMENTATION.md` with HSTS clearing instructions
- Provided browser-specific steps to clear HSTS cache

## Tasks Completed
- [x] Analyze the redirection issue
- [x] Identify root cause (browser HSTS cache)
- [x] Update documentation with HSTS clearing instructions
- [x] Provide verification steps

## Next Steps
Clear browser HSTS cache for localhost:
- **Chrome/Edge**: Go to `chrome://net-internals/#hsts`, query "localhost", click "Delete"
- **Firefox**: Open Developer Tools (F12) → Network tab → Right-click any request → "Disable HTTP Strict Transport Security"
- **Safari**: Clear browsing data or use private browsing mode

Additional troubleshooting if HSTS clearing doesn't work:
1. **Clear all browser data for localhost**:
   - Chrome: Settings → Privacy → Clear browsing data → Advanced → Time range: All time → Cookies, Cached images, Hosted app data
   - Or use incognito/private browsing mode

2. **Check for cached 301 redirects**:
   - Open Developer Tools (F12) → Network tab
   - Check if there's a 301 redirect response
   - Clear network cache if available

3. **Try a different browser** or create a new browser profile

4. **Check for proxy/VPN**: Disable any proxy or VPN that might be redirecting

5. **Verify DEBUG setting**: Ensure DEBUG=True in environment or .env file

## Verification
- Access `http://127.0.0.1:8000/` directly without redirection to HTTPS
- Confirm the application loads properly in development mode
