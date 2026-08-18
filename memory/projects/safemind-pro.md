# SafeMind.pro — Recovery Log & Server Settings

**Date:** 2026-08-16 ~ 2026-08-17
**Server:** Nimble Cepheus (Timeweb Cloud)
**IP:** 200.165.227.84
**Domain:** safemind.pro
**Root Password:** gN8J__WG#P88wf
**Node:** kvmnvm-737
**IPv6:** 2a03:6f00:a::2:1bf7

---

## What Happened (Incident)

1. **Initial Problem:** Website safemind.pro was down (502 Bad Gateway)
2. **Root Cause:** Server was offline / SSH port 22 closed
3. **Secondary Issue:** DNS A-record pointed to old IP `85.239.59.8` instead of current `200.165.227.84`

---

## Recovery Steps (What Worked)

### Step 1: Server Power Cycle
- Timeweb Cloud panel → Server Nimble Cepheus → **Hard Reboot**
- First soft reboot didn't help (server hung during boot with systemd logs visible in VNC console)
- **Solution:** Full power off → wait 10s → power on
- After hard reboot server came back online

### Step 2: Verify SSH Access
```bash
ssh root@200.165.227.84
# Password: gN8J__WG#P88wf
```
- SSH port 22 was closed initially due to server being down, NOT firewall
- Timeweb Cloud closed ports: 2525, 3389, 465, 25, 389, 587, 53413
- Port 22 was NOT in closed list ✅

### Step 3: Check Nginx
```bash
systemctl status nginx
# Result: active (running)
```
- Nginx started automatically after reboot
- Listening on 0.0.0.0:80 and 0.0.0.0:443

### Step 4: Fix DNS
- **Registrar/DNS:** REG.RU (ns1.reg.ru, ns2.reg.ru)
- **Old A-record:** 85.239.59.8 ❌
- **New A-record:** 200.165.227.84 ✅
- **Action:** Login to REG.RU → Domain management → DNS records → Change A-record
- **Propagation time:** ~5-15 minutes

### Step 5: Verify Website
```bash
curl -s -o /dev/null -w "%{http_code}" https://safemind.pro
# Result: 200 OK ✅
```

---

## Server Configuration

### Nginx Config
Location: `/etc/nginx/sites-enabled/safemind`

```nginx
server {
    listen 80;
    server_name safemind.pro www.safemind.pro;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name safemind.pro www.safemind.pro;
    root /opt/safemind;
    index index.html;

    ssl_certificate /etc/letsencrypt/live/safemind.pro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/safemind.pro/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/safemind.pro/chain.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    location / { try_files $uri $uri/ =404; }

    location /api {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~ ^/(health|subscribe|leads|trigger-drip|download) {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /pdfs/ { alias /opt/safemind/pdfs/; }
    location /assets/ { alias /opt/safemind/assets/; }

    location /admin {
        proxy_pass http://127.0.0.1:3002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Also includes separate server block for kadena-game on IP 85.239.59.8 (port 80, /api proxied to :8000)

### SSL Certificate
- **Provider:** Let's Encrypt
- **Path:** `/etc/letsencrypt/live/safemind.pro/`
- **Valid:** Jun 26, 2026 → Sep 24, 2026
- **Auto-renewal:** Should be configured via certbot

### Backend Services (Running Locally)
| Port | Service | Description |
|------|---------|-------------|
| 3001 | Main API | `location /api` |
| 3002 | Admin Panel | `location /admin` |
| 8002 | Marketing APIs | health, subscribe, leads, trigger-drip, download |

### Firewall (UFW)
```
Status: active
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
8080/tcp                   ALLOW       Anywhere
```

### Website Root
```
/opt/safemind/
├── index.html
├── pdfs/
└── assets/
```

---

## DNS Settings

| Record | Type | Value | TTL |
|--------|------|-------|-----|
| @ | A | 200.165.227.84 | Default |
| www | CNAME or A | safemind.pro or 200.165.227.84 | Default |

**DNS Provider:** REG.RU (ns1.reg.ru, ns2.reg.ru)

---

## Quick Recovery Checklist (If Site Goes Down Again)

1. **Check server status in Timeweb panel**
   - URL: https://timeweb.cloud/my/servers/7719921
   - Look for: "В сети" vs "Выключен"

2. **If server is OFF → Power cycle**
   - Button: Power OFF → wait 10s → Power ON
   - Wait 2-3 minutes for boot

3. **Verify SSH**
   ```bash
   ssh root@200.165.227.84
   # Password: gN8J__WG#P88wf
   ```

4. **Check nginx status**
   ```bash
   systemctl status nginx
   systemctl restart nginx  # if needed
   ```

5. **Verify from inside server**
   ```bash
   curl -I http://localhost/
   curl -I https://localhost/  # might fail SSL locally
   ```

6. **Check DNS**
   ```bash
   dig +short safemind.pro
   # Should return: 200.165.227.84
   ```

7. **Verify from outside**
   ```bash
   curl -I https://safemind.pro
   # Should return: HTTP/2 200
   ```

---

## Important Notes

- **Timeweb Cloud credentials** were used for browser automation during recovery → consider changing password for security
- **Backup strategy:** Consider setting up automated backups in Timeweb panel (Backups tab)
- **Monitoring:** Could set up uptime monitoring (e.g., UptimeRobot) to get alerts when site is down
- **SSL renewal:** Check auto-renewal before Sep 24, 2026

---

## Related Projects

- Server also runs `kadena-game` on port 80 for IP 85.239.59.8 (legacy config)
- Separate backend services on ports 3001, 3002, 8002

