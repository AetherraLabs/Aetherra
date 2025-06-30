# 🌐 Custom Domain Setup Guide

## CNAME File Configuration

### Current Setup
- **Domain**: httpsneurocode.dev
- **Temporary Domain**: https://c4e0fc07.neurocode-website.pages.dev/
- **Files Created**: 
  - `/CNAME` (for root deployment)
  - `/website/CNAME` (for website folder deployment)

### To Change Domain
Edit the CNAME file(s) to contain your domain:
```
yourdomain.com
```

### Common Domain Options
```bash
# Example domains (choose one):
neurocode.dev
neurocode.ai
neurocode.io
neuroplexai.com
ai-neurocode.dev
```

## DNS Configuration Required

### For Cloudflare + GitHub Pages:

#### Required Records:
1. **A Record** (for root domain):
   - **Type**: A
   - **Name**: `@` (this represents the root domain)
   - **Content/Target**: `185.199.108.153`
   - **Proxy Status**: ✅ Proxied (Orange cloud)

2. **Additional A Records** (add these too):
   - **Type**: A, **Name**: `@`, **Content**: `185.199.109.153`
   - **Type**: A, **Name**: `@`, **Content**: `185.199.110.153`
   - **Type**: A, **Name**: `@`, **Content**: `185.199.111.153`

3. **CNAME Record** (for www subdomain):
   - **Type**: CNAME
   - **Name**: `www`
   - **Content/Target**: `zyonic88.github.io`
   - **Proxy Status**: ✅ Proxied (Orange cloud)

#### ✅ Your Current Setup is CORRECT!
```
A       httpsneurocode.dev   185.199.111.153   ✅ CORRECT
A       httpsneurocode.dev   185.199.110.153   ✅ CORRECT
A       httpsneurocode.dev   185.199.109.153   ✅ CORRECT
A       httpsneurocode.dev   185.199.108.153   ✅ CORRECT
CNAME   www                  zyonic88.github.io ✅ CORRECT
```

#### 🎉 Perfect! Your DNS is set up correctly!

#### ✅ What you should see in Cloudflare:
```
Type    Name    Content               Proxy Status
A       @       185.199.108.153      ✅ Proxied
A       @       185.199.109.153      ✅ Proxied  
A       @       185.199.110.153      ✅ Proxied
A       @       185.199.111.153      ✅ Proxied
CNAME   www     zyonic88.github.io   ✅ Proxied
```

#### 🛠️ Fix Steps:
1. **DELETE** the current CNAME record (`httpsneurocode.dev → neurocode.dev`)
2. **ADD** 4 A records as shown above
3. **ADD** 1 CNAME record for `www` → `zyonic88.github.io`

### For Other Hosting:
1. **CNAME Record**: `www` → `your-hosting-provider.com`
2. **A Record**: `@` → `your-server-ip`

## GitHub Pages Setup Steps

### ✅ EXCELLENT! GitHub Pages is Now CONFIGURED CORRECTLY!

Based on your latest screenshot, everything is set up perfectly:

✅ **GitHub Pages**: Enabled and deploying from `main` branch  
✅ **Custom Domain**: `httpsneurocode.dev` configured  
✅ **DNS Check**: Successful (green checkmark)  
✅ **HTTPS**: Available but currently unavailable (will be enabled once domain propagates)  

### 🎯 Current Status:
- **Source**: Deploy from `main` branch, `/ (root)` folder ✅
- **Custom Domain**: `httpsneurocode.dev` ✅ 
- **DNS**: Successfully configured ✅
- **HTTPS**: Will be available shortly (waiting for domain verification)

### � CRITICAL ISSUE IDENTIFIED!

**Problem**: GitHub Pages is serving `README.md` (Jekyll), not `website/index.html`

**What's happening**:
- ✅ Your `website/index.html` has correct GitHub links
- ❌ GitHub Pages is serving the Jekyll-generated `README.md` instead
- ❌ The Jekyll site might have cached/old GitHub links

**IMMEDIATE FIX NEEDED**:

### ✅ SOLUTION IMPLEMENTED!

**What we just did:**
1. ✅ **Moved custom website files** from `/website/` to root directory
2. ✅ **Backed up README.md** as `README_original.md`
3. ✅ **Your custom `index.html`** is now in the root
4. ✅ **Committed and pushed** changes to GitHub

**Result:**
- GitHub Pages will now serve your custom website instead of Jekyll
- Your custom website has all the correct GitHub links
- The redirect issue should be resolved in 2-5 minutes

### 🎯 What to expect:
- **Wait 2-5 minutes** for GitHub Pages to rebuild
- **Visit `https://httpsneurocode.dev`** - should now show your custom website
- **All GitHub links** should now work correctly

## Verification Commands (PowerShell)

```powershell
# Check DNS propagation
nslookup httpsneurocode.dev

# Test CNAME resolution  
nslookup www.httpsneurocode.dev

# Verify GitHub Pages (use Invoke-WebRequest instead of curl)
Invoke-WebRequest -Uri "https://httpsneurocode.dev" -Method Head

# Alternative: Test if site is responding
Test-NetConnection httpsneurocode.dev -Port 443
```

## Troubleshooting Commands (PowerShell)

```powershell
# Force refresh DNS cache
ipconfig /flushdns

# Check if GitHub Pages is serving content
$response = Invoke-WebRequest -Uri "https://httpsneurocode.dev" -UseBasicParsing
$response.StatusCode
$response.Headers

# Test connection to GitHub's servers
Test-NetConnection github.io -Port 443

# Check if CNAME file exists in repository
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Zyonic88/NeuroCode/main/CNAME" -UseBasicParsing

# Test with different DNS servers
nslookup httpsneurocode.dev 8.8.8.8
nslookup httpsneurocode.dev 1.1.1.1
```

## Notes

- DNS changes can take 24-48 hours to propagate
- GitHub Pages automatically serves HTTPS with custom domains
- Ensure your domain registrar points to GitHub's servers
