# 🔒 Security Deployment Guide - WaterBilling

## Pre-Deployment Checklist

### ✅ Critical Fixes Applied
- [x] **Fix #1:** SECRET_KEY now requires environment variable (no fallback)
- [x] **Fix #2:** DEBUG mode controlled via environment variable
- [x] **Fix #3:** HTTPS security headers enabled
- [x] **Fix #4:** Django updated to 5.0.1
- [x] **Fix #5:** OTP rate limiting and expiration implemented

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Generate SECRET_KEY

Run this command locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output (50+ character random string) and save it.

### Step 2: Set Environment Variables

For **Render.com** deployment:

1. Go to your Render service
2. Click "Environment"
3. Add these variables:

```
SECRET_KEY=<your-generated-secret-key-from-step-1>
DEBUG=False
ALLOWED_HOSTS=waterbilling-r92q.onrender.com,yourdomain.com
CSRF_TRUSTED_ORIGINS=https://waterbilling-r92q.onrender.com
CORS_ALLOWED_ORIGINS=https://waterbilling-r92q.onrender.com
DATABASE_URL=<your-database-url>
OTP=True
OTP_EMAIL=your-email@gmail.com
OTP_PASSWORD=your-app-password
STRIPE_PUBLIC_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
```

### Step 3: Update Dependencies

```bash
pip install -r requirements.txt
```

The requirements now include:
- Django 5.0.1 (CVE-free version)
- All dependencies with security patches

### Step 4: Run Migrations

```bash
python manage.py migrate
```

This creates the new OTP security fields:
- `otp_created_at` - Timestamp for OTP expiration
- `otp_attempts` - Failed attempt counter for rate limiting

### Step 5: Verify Settings

```bash
python manage.py check --deploy
```

Expected output:
- No CRITICAL errors
- Only informational messages

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 7: Deploy

Push to your Render branch or redeploy manually.

---

## 🔐 Security Features Implemented

### 1. **Secret Key Management**
- No hardcoded secrets
- Requires environment variable
- Fails fast if not provided
- 50+ character entropy requirement

### 2. **DEBUG Mode Protection**
```python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```
- Defaults to False (safe)
- Only enabled with explicit environment variable
- Production deployment should have DEBUG=False

### 3. **HTTPS & Security Headers**
```
SECURE_SSL_REDIRECT = True              # Force HTTPS
SESSION_COOKIE_SECURE = True            # Secure session cookies
CSRF_COOKIE_SECURE = True               # Secure CSRF cookies
SECURE_HSTS_SECONDS = 31536000          # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # Include subdomains
X_FRAME_OPTIONS = 'DENY'                # Prevent clickjacking
SECURE_BROWSER_XSS_FILTER = True        # XSS protection
```

### 4. **OTP Security**
- **Expiration:** 10-minute validity
- **Rate Limiting:** Maximum 5 failed attempts
- **Timing Attack Protection:** Uses constant_time_compare()
- **Failed Attempt Tracking:** Resets on successful login
- **Attempt Logging:** Failed attempts tracked in database

### 5. **Email Enumeration Prevention**
- Same response for valid/invalid emails in password reset
- Prevents user enumeration attacks
- Error messages don't leak user existence

### 6. **Environment Variable Configuration**
- All hosts, CORS origins, and trusted origins from env vars
- No hardcoded domains
- Supports comma-separated values for multiple origins

---

## 📊 OTP Security Parameters

```python
OTP_EXPIRY_MINUTES = 10       # OTP valid for 10 minutes
OTP_MAX_ATTEMPTS = 5          # 5 failed attempts allowed
```

After 5 failed attempts, user must request a new OTP.

---

## 🔍 Post-Deployment Verification

### 1. Test HTTPS Redirect
```bash
curl -I http://yourdomain.com
# Should redirect to https
```

### 2. Check Security Headers
```bash
curl -I https://yourdomain.com
# Should include:
# - Strict-Transport-Security
# - X-Frame-Options: DENY
# - X-XSS-Protection
```

### 3. Test OTP Expiration
1. Login as user
2. Request OTP
3. Wait 11+ minutes
4. Try to verify OTP
5. Should fail with "OTP has expired"

### 4. Test OTP Rate Limiting
1. Login as user
2. Request OTP
3. Try 6 wrong codes
4. Should be blocked after 5 attempts

### 5. Verify Django Version
```bash
python manage.py shell
>>> import django
>>> print(django.__version__)
5.0.1
```

---

## 🛠️ Troubleshooting

### "SECRET_KEY environment variable not set"
**Solution:** Add SECRET_KEY to environment variables

### "DEBUG Mode Warning"
**Solution:** Ensure DEBUG=False in production

### "HTTPS Not Redirecting"
**Solution:** Check SECURE_SSL_REDIRECT and SSL certificate

### "OTP Not Working"
**Solution:** Check email configuration and OTP settings

### Migration Errors
**Solution:**
```bash
python manage.py showmigrations
python manage.py migrate --fake account 0004
python manage.py migrate account
```

---

## 📝 Ongoing Security Maintenance

### Weekly
- [ ] Monitor application logs for errors
- [ ] Check for failed login attempts
- [ ] Review Django security announcements

### Monthly
- [ ] Update dependencies: `pip list --outdated`
- [ ] Review error logs
- [ ] Test backup/restore procedures

### Quarterly
- [ ] Security audit of access logs
- [ ] Penetration testing
- [ ] Review compliance requirements

---

## 🔗 Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/5.0/topics/security/)
- [OWASP Security Guidelines](https://owasp.org/)
- [Safety.io Dependency Check](https://safety.io/)

---

## 📞 Emergency Contacts

If you experience security issues:
1. Take the application offline
2. Contact your security team
3. Review audit logs
4. Follow incident response procedures

---

**Last Updated:** 2026-02-04
**Version:** 1.0
**Status:** Ready for Deployment ✅
