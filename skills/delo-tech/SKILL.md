# delo-tech

**Skill for automating access to ДЕЛО ТЕХ (rlisystems.ru/conterra/) personal cabinet.**

## Description

Automates login and basic navigation in the "ДЕЛО ТЕХ" system (RLISystems / Контейнерный терминал). Used for logistics and customs document management.

## Triggers

- User mentions: "delo tech", "дело тех", "rlisystems", "conterra", "контейнерный терминал"
- Request to check container status, release orders, balance

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This documentation |
| `delo_tech.py` | Python module for automation |
| `.env.example` | Environment variables template |
| `requirements.txt` | Python dependencies |

## Setup

1. Copy `.env.example` to `.env` and fill credentials:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # Or for Playwright:
   # playwright install chromium
   ```

## Usage

### From Python
```python
from delo_tech import DeloTechClient

client = DeloTechClient()
client.login()
dashboard = client.get_dashboard()
print(dashboard)
```

### From CLI
```bash
python delo_tech.py --action login
python delo_tech.py --action balance
python delo_tech.py --action orders
```

## Architecture

The site uses:
- Main page: `https://rlisystems.ru/conterra/` (iframe with login form)
- Direct SSO: `https://rlisystems.ru/webiom/sso/`
- After login: redirect to personal cabinet with release orders, balance, terminal info

## Security Notes

- Credentials stored in `.env` (gitignored by default)
- All operations use HTTPS
- Session cookies stored in memory only (not persisted)

## Expansion Plans

- [ ] Parse release orders (релиз-ордера)
- [ ] Check container status by number
- [ ] Download customs documents
- [ ] Balance tracking and alerts
- [ ] Integration with Telegram notifications

## Author

Created for Artur A.
