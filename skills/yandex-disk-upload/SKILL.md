# Skill: Yandex Disk Upload

## Purpose
Upload files to Yandex Disk (Яндекс.Диск) from OpenClaw workspace.

## Setup

1. Get OAuth token from Yandex:
   - Go to: https://yandex.ru/dev/disk/poligon/
   - Click "Получить OAuth-токен"
   - Authorize with your Yandex account
   - Copy the token (long string like `y0_Ag...`)

2. Save token to `.env` file:
   ```bash
   echo "YANDEX_DISK_TOKEN=your_token_here" >> ~/.openclaw/workspace/.env
   ```

3. Or provide token to this skill and it will save it securely.

## Usage

```bash
# Upload a single file to Yandex Disk root
python skills/yandex-disk-upload/upload.py /path/to/file.pdf

# Upload to a specific folder
python skills/yandex-disk-upload/upload.py /path/to/file.pdf --folder /MarketPlays

# Upload multiple files
python skills/yandex-disk-upload/upload.py file1.pdf file2.pdf --folder /MarketPlays
```

## API Reference

Base URL: `https://cloud-api.yandex.net/v1/disk`

Endpoints used:
- `GET /disk/resources/upload` — get upload URL
- `PUT {upload_url}` — upload file content
- `PUT /disk/resources` — create folder if not exists

## Notes
- Token must have `cloud_api:disk.write` permission
- Files are uploaded to the root of Yandex Disk by default
- Folder path is created automatically if it doesn't exist
