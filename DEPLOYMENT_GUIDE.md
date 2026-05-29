# Deployment Guide - Encrypted Messaging System

Complete guide for deploying the encrypted messaging system to production.

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Security Checklist](#security-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)

## 🏠 Local Development

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Git
- Virtual environment (recommended)

### Step 1: Clone and Setup Backend

```bash
# Clone repository
git clone <repo-url>
cd new

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./messages.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
ENCRYPTION_KEY=default-key-32-bytes-long-123456
EOF

# Run backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Setup Frontend

```bash
# In new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
EOF

# Start development server
npm start
```

The application will open at `http://localhost:3000`

## 🚀 Production Deployment

### Prerequisites
- Ubuntu 20.04 LTS or similar
- Domain name (optional)
- SSL certificate (for HTTPS)
- Nginx (reverse proxy)
- PostgreSQL (database)

### Backend Production Setup

#### 1. Install System Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.9 python3.9-venv python3-pip
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx
sudo apt install -y supervisor
```

#### 2. Setup PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In psql console:
CREATE DATABASE encrypted_messaging;
CREATE USER messaging_user WITH PASSWORD 'strong_password_here';
ALTER ROLE messaging_user SET client_encoding TO 'utf8';
ALTER ROLE messaging_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE messaging_user SET default_transaction_deferrable TO on;
ALTER ROLE messaging_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE encrypted_messaging TO messaging_user;
\q
```

#### 3. Deploy Application

```bash
# Create app directory
sudo mkdir -p /var/www/encrypted-messaging
sudo chown -R $USER:$USER /var/www/encrypted-messaging
cd /var/www/encrypted-messaging

# Clone repository
git clone <repo-url> .

# Setup virtual environment
cd backend
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn python-dotenv

# Create .env file (update with real values)
cat > .env << EOF
DATABASE_URL=postgresql://messaging_user:strong_password_here@localhost/encrypted_messaging
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
ENCRYPTION_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
DEBUG=False
EOF
```

#### 4. Setup Systemd Service

```bash
# Create systemd service file
sudo tee /etc/systemd/system/encrypted-messaging.service > /dev/null << EOF
[Unit]
Description=Encrypted Messaging FastAPI Application
After=network.target postgresql.service

[Service]
Type=notify
User=$USER
WorkingDirectory=/var/www/encrypted-messaging/backend
Environment="PATH=/var/www/encrypted-messaging/backend/venv/bin"
ExecStart=/var/www/encrypted-messaging/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable encrypted-messaging
sudo systemctl start encrypted-messaging
sudo systemctl status encrypted-messaging
```

#### 5. Setup Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/encrypted-messaging > /dev/null << EOF
upstream fastapi {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # API endpoints
    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable configuration
sudo ln -s /etc/nginx/sites-available/encrypted-messaging /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### 6. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Frontend Production Setup

#### 1. Build React Application

```bash
cd /var/www/encrypted-messaging/frontend

# Install dependencies
npm install

# Build for production
npm run build

# The build/ directory contains static files for deployment
```

#### 2. Setup Nginx for Frontend

```bash
# Update Nginx configuration to serve React app
sudo tee /etc/nginx/sites-available/encrypted-messaging-frontend > /dev/null << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    root /var/www/encrypted-messaging/frontend/build;
    index index.html;
    
    # React Router support
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket proxy
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo nginx -t
sudo systemctl restart nginx
```

## 🐳 Docker Deployment

### Docker Setup

#### 1. Create Dockerfile for Backend

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create Dockerfile for Frontend

```dockerfile
# frontend/Dockerfile
FROM node:14-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 3. Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: encrypted_messaging
      POSTGRES_USER: messaging_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      DATABASE_URL: postgresql://messaging_user:your_secure_password@db:5432/encrypted_messaging
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      CORS_ORIGINS: '["http://localhost:3000", "http://localhost:80"]'
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      REACT_APP_API_URL: http://localhost:8000
      REACT_APP_WS_URL: ws://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

#### 4. Deploy with Docker

```bash
# Create .env file
cat > .env << EOF
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
ENCRYPTION_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
EOF

# Build and start containers
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## ✅ Security Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Use strong database password
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Enable firewall rules
- [ ] Setup rate limiting
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Implement 2FA
- [ ] Use environment variables for secrets
- [ ] Regular security audits
- [ ] Implement DDoS protection
- [ ] Setup intrusion detection

## 🔍 Monitoring & Maintenance

### View Application Logs

```bash
# Systemd service logs
sudo journalctl -u encrypted-messaging -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
tail -f /var/log/encrypted-messaging/app.log
```

### Database Backup

```bash
# Backup database
sudo -u postgres pg_dump encrypted_messaging > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql encrypted_messaging < backup_20231201_120000.sql
```

### Application Updates

```bash
cd /var/www/encrypted-messaging

# Pull latest code
git pull origin main

# Update dependencies
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart encrypted-messaging

# Frontend updates
cd frontend
npm install
npm run build
sudo systemctl restart nginx
```

## 📊 Performance Optimization

1. **Enable Caching**:
   - Static file caching in Nginx
   - API response caching
   - Browser caching headers

2. **Database Optimization**:
   - Add indexes to frequently queried columns
   - Regular VACUUM and ANALYZE
   - Connection pooling

3. **Application**:
   - Use CDN for static assets
   - Implement message pagination
   - Optimize database queries

4. **Server**:
   - Adjust worker count
   - Enable gzip compression
   - Use SSD storage

## 📞 Troubleshooting

```bash
# Check service status
sudo systemctl status encrypted-messaging

# Restart service
sudo systemctl restart encrypted-messaging

# Check Nginx
sudo nginx -t
sudo systemctl restart nginx

# View system logs
sudo dmesg

# Check disk space
df -h

# Check memory
free -h
```

---

For more information, see [Encrypted Messaging System README](./MESSAGING_SYSTEM_README.md)
