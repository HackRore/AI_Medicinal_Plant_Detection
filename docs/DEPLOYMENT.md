# Production Deployment Guide

## 🚀 Complete Deployment Instructions

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed  
- Docker and Docker Compose (for containerized deployment)
- Git

---

## Quick Deploy (Automated)

### Windows
```powershell
# Run the automated deployment script
.\deploy.ps1
```

### Linux/Mac
```bash
# Run the automated deployment script
chmod +x deploy.sh
./deploy.sh
```

This will:
- ✅ Set up ML model configurations
- ✅ Install all dependencies
- ✅ Seed the database
- ✅ Create environment files
- ✅ Prepare for deployment

---

## Manual Deployment Steps

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.production .env
# Edit .env with your production values

# Seed database
python scripts/seed_data.py

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "API_URL=http://localhost:8000" > .env.local

# Build for production
npm run build

# Start production server
npm start
```

### 3. ML Models Setup

```bash
cd ml_pipeline

# Quick setup (creates config files)
python quick_setup.py

# Copy to backend
copy models\* ..\backend\ml_models\

# Optional: Train real models (requires dataset)
# pip install -r requirements.txt
# python train_mobilenet.py
```

---

## Docker Deployment (Recommended)

### Development
```bash
cd infrastructure/docker
docker-compose up -d
```

### Production
```bash
cd infrastructure/docker
docker-compose -f docker-compose.prod.yml up -d
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Cloud Deployment

### AWS (Elastic Beanstalk)

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
eb init -p docker medicinal-plant-api
```

3. Create environment:
```bash
eb create production
```

4. Deploy:
```bash
eb deploy
```

### Google Cloud (Cloud Run)

1. Build and push:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/medicinal-plant-api
```

2. Deploy:
```bash
gcloud run deploy medicinal-plant-api \
  --image gcr.io/PROJECT_ID/medicinal-plant-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku

1. Create app:
```bash
heroku create medicinal-plant-api
```

2. Add PostgreSQL:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

3. Deploy:
```bash
git push heroku main
```

### DigitalOcean (Droplet)

1. Create droplet with Docker
2. SSH into droplet
3. Clone repository
4. Run docker-compose:
```bash
git clone <repo>
cd AI_Medicinal_Plant_Detection/infrastructure/docker
docker-compose -f docker-compose.prod.yml up -d
```

---

## Production Checklist

### Security
- [ ] Change SECRET_KEY in .env
- [ ] Update ALLOWED_ORIGINS
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Set up rate limiting
- [ ] Implement authentication

### Database
- [ ] Switch to PostgreSQL
- [ ] Set up backups
- [ ] Configure connection pooling
- [ ] Enable SSL connections

### Performance
- [ ] Enable Redis caching
- [ ] Configure CDN for static files
- [ ] Set up load balancing
- [ ] Enable gzip compression

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Enable performance monitoring

### ML Models
- [ ] Train models with real dataset
- [ ] Export to ONNX format
- [ ] Copy to backend/ml_models/
- [ ] Test predictions

---

## Environment Variables

### Required
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=<generate-strong-key>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Optional
```env
GEMINI_API_KEY=<your-key>
REDIS_URL=redis://localhost:6379/0
SENTRY_DSN=<your-dsn>
```

---

## Troubleshooting

### Backend won't start
- Check Python version (3.10+)
- Verify all dependencies installed
- Check database connection
- Review logs: `tail -f backend/logs/app.log`

### Frontend build fails
- Clear cache: `rm -rf .next node_modules`
- Reinstall: `npm install`
- Check Node version (18+)

### Database errors
- Verify DATABASE_URL
- Check PostgreSQL is running
- Run migrations
- Reseed if needed

### ML predictions fail
- Ensure models exist in ml_models/
- Check class_names.json exists
- Verify ONNX runtime installed

---

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.prod.yml
backend:
  deploy:
    replicas: 3
```

### Load Balancer
Use Nginx or cloud load balancer to distribute traffic.

### Database Scaling
- Read replicas for queries
- Connection pooling
- Caching with Redis

---

## Backup Strategy

### Database
```bash
# Backup
pg_dump medicinal_plants_db > backup.sql

# Restore
psql medicinal_plants_db < backup.sql
```

### Files
```bash
# Backup uploads
tar -czf uploads_backup.tar.gz backend/uploads/

# Restore
tar -xzf uploads_backup.tar.gz
```

---

## Monitoring

### Health Checks
- Backend: http://your-domain/health
- Database: Check connection
- Redis: `redis-cli ping`

### Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend
```

---

## Support

For deployment issues:
- Check documentation in `docs/`
- Review error logs
- Contact: hackrore@gmail.com
