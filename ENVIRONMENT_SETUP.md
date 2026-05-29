# Environment Setup Guide

Configuration and environment variables for the encrypted messaging system.

## 🔧 Backend Configuration

### Backend `.env` File

Create `backend/.env`:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./messages.db
# For PostgreSQL in production:
# DATABASE_URL=postgresql://user:password@localhost:5432/encrypted_messaging

# Security - Generate new keys for production!
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Add your frontend URL
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://localhost"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Encryption
ENCRYPTION_KEY=default-key-32-bytes-long-123456

# Optional: API Settings
DEBUG=False
LOG_LEVEL=INFO
```

### Generate Strong Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | `sqlite:///./messages.db` | Database connection URL |
| `SECRET_KEY` | string | `your-secret-key-...` | JWT signing key |
| `ALGORITHM` | string | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Token expiration time |
| `CORS_ORIGINS` | list | `["http://localhost:3000"]` | Allowed CORS origins |
| `ALLOWED_HOSTS` | list | `["localhost"]` | Allowed host headers |
| `ENCRYPTION_KEY` | string | `default-key-...` | Message encryption key |
| `DEBUG` | bool | `False` | Debug mode |

## 🎨 Frontend Configuration

### Frontend `.env` File

Create `frontend/.env`:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Optional: Analytics
# REACT_APP_ANALYTICS_ID=your-analytics-id
```

### Production `.env.production`

```bash
REACT_APP_API_URL=https://your-domain.com
REACT_APP_WS_URL=wss://your-domain.com
```

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REACT_APP_API_URL` | string | `http://localhost:8000` | Backend API URL |
| `REACT_APP_WS_URL` | string | `ws://localhost:8000` | WebSocket URL |

## 🐳 Docker Configuration

### Docker Environment

Create `.env` for Docker Compose:

```bash
# Database
DB_USER=messaging_user
DB_PASSWORD=secure_password_123
DB_NAME=encrypted_messaging

# Backend
BACKEND_SECRET_KEY=your-secret-key-change-in-production
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost"]

# Frontend
FRONTEND_API_URL=http://localhost:8000
FRONTEND_WS_URL=ws://localhost:8000
```

### Docker Compose Override

Create `docker-compose.override.yml` for development:

```yaml
version: '3.8'

services:
  backend:
    environment:
      DEBUG: 'True'
      LOG_LEVEL: DEBUG
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    environment:
      CI: 'false'
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
```

## 🌐 Production Environment

### Linux/Ubuntu

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@db-server:5432/encrypted_messaging"
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
export ENCRYPTION_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
export CORS_ORIGINS='["https://your-domain.com"]'

# Run application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Systemd Service

Create `/etc/systemd/system/encrypted-messaging.service`:

```ini
[Unit]
Description=Encrypted Messaging Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/encrypted-messaging
Environment="DATABASE_URL=postgresql://..."
Environment="SECRET_KEY=..."
Environment="ENCRYPTION_KEY=..."
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔐 Security Environment Variables

### Development (NOT FOR PRODUCTION)

```bash
# Minimal security (for testing only)
SECRET_KEY=dev-key-not-secure
ENCRYPTION_KEY=dev-encryption-key
DEBUG=True
```

### Production (MUST CHANGE)

```bash
# Strong security settings
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
ENCRYPTION_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
DEBUG=False

# Strong database password
DB_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')

# HTTPS only
CORS_ORIGINS=["https://your-domain.com"]
SECURE_COOKIES=True
HTTPS_ONLY=True
```

## 📝 Configuration Examples

### Local Development

```bash
# backend/.env
DATABASE_URL=sqlite:///./messages.db
SECRET_KEY=dev-secret-key-123456789012345678
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
DEBUG=True
```

```bash
# frontend/.env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Staging

```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@staging-db:5432/encrypted_messaging
SECRET_KEY=staging-secret-key-strong-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["https://staging.example.com"]
DEBUG=False
```

```bash
# frontend/.env
REACT_APP_API_URL=https://staging.example.com
REACT_APP_WS_URL=wss://staging.example.com
```

### Production

```bash
# backend/.env
DATABASE_URL=postgresql://secure_user:STRONG_PASSWORD@prod-db:5432/encrypted_messaging
SECRET_KEY=GENERATED_SECRET_KEY_STRONG_RANDOM_STRING
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://your-domain.com", "https://www.your-domain.com"]
DEBUG=False
LOG_LEVEL=WARNING
```

```bash
# frontend/.env.production
REACT_APP_API_URL=https://your-domain.com
REACT_APP_WS_URL=wss://your-domain.com
```

## 🔄 Environment Variables in Docker

### Docker Compose

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - DEBUG=${DEBUG}
```

### Build-time Variables

```bash
# Build with environment
docker build \
  --build-arg DATABASE_URL=postgresql://... \
  --build-arg SECRET_KEY=... \
  -t encrypted-messaging:latest .
```

## ✅ Verification Checklist

- [ ] `backend/.env` created and configured
- [ ] `frontend/.env` created and configured
- [ ] `SECRET_KEY` changed from default
- [ ] `ENCRYPTION_KEY` changed from default
- [ ] Database URL correct
- [ ] CORS origins include your domain
- [ ] All required variables set
- [ ] No sensitive data in version control
- [ ] `.env` files added to `.gitignore`

## 🚨 Important Notes

1. **Never commit `.env` files** to version control
2. **Always use strong random keys** in production
3. **Change default values** before deploying
4. **Use HTTPS/WSS** in production
5. **Keep sensitive data** in environment variables
6. **Rotate keys** periodically
7. **Monitor logs** for security issues
8. **Use secrets management** for sensitive data (HashiCorp Vault, AWS Secrets Manager, etc.)

## 🔗 Related Documentation

- [QUICKSTART.md](./QUICKSTART.md) - Quick setup guide
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production deployment
- [README.md](./README.md) - Main documentation

---

For more information, see the documentation files or contact support.
