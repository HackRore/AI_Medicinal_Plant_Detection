# 🧪 Complete Testing Guide

## Web Testing (Browser)

### Quick Start - Test Locally

1. **Start Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start Frontend:**
```bash
cd frontend
npm run dev
```

3. **Access in Browser:**
- **Main App:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Test on Mobile Browser (Same Network)

1. Find your computer's IP address:
```bash
# Windows
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

2. Update frontend `.env.local`:
```env
API_URL=http://YOUR_IP:8000
NEXT_PUBLIC_API_URL=http://YOUR_IP:8000
```

3. Access from phone browser:
```
http://YOUR_IP:3000
```

### Test Features

#### ✅ Landing Page
- [ ] Hero section loads
- [ ] Feature cards display
- [ ] Navigation works
- [ ] Responsive on mobile

#### ✅ Prediction Page
- [ ] Image upload works
- [ ] Drag-and-drop works
- [ ] Prediction displays
- [ ] Confidence bar shows
- [ ] Top predictions list

#### ✅ API Endpoints
- [ ] GET /api/v1/plants/ - List plants
- [ ] GET /api/v1/plants/1 - Get plant details
- [ ] POST /api/v1/predict/ - Upload image
- [ ] GET /api/v1/recommend/similar/1 - Recommendations

---

## Mobile App Testing (APK)

### Option 1: React Native Expo (Recommended)

#### Setup
```bash
cd mobile
npx create-expo-app@latest . --template blank-typescript
npm install
```

#### Configure API
Edit `app.json`:
```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://YOUR_IP:8000"
    }
  }
}
```

#### Test on Phone
```bash
# Install Expo Go app on your phone
# Then run:
npx expo start

# Scan QR code with Expo Go
```

#### Build APK
```bash
# For Android
eas build --platform android --profile preview

# Or local build
npx expo build:android
```

### Option 2: PWA (Progressive Web App)

Convert the Next.js app to PWA for mobile testing:

1. **Install PWA plugin:**
```bash
cd frontend
npm install next-pwa
```

2. **Update `next.config.js`:**
```javascript
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
})

module.exports = withPWA({
  // existing config
})
```

3. **Add manifest.json** in `public/`:
```json
{
  "name": "Medicinal Plant Detection",
  "short_name": "Plant AI",
  "description": "AI-powered medicinal plant identification",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#22c55e",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

4. **Test PWA:**
- Open in Chrome mobile
- Menu → "Add to Home Screen"
- Opens like native app!

---

## Deployment for Public Testing

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Deploy Frontend to Vercel:
```bash
cd frontend
npm install -g vercel
vercel
```

#### Deploy Backend to Railway:
1. Go to railway.app
2. Connect GitHub repo
3. Deploy backend folder
4. Get public URL

#### Update Frontend:
```env
API_URL=https://your-backend.railway.app
```

### Option 2: Netlify + Render

#### Frontend (Netlify):
```bash
cd frontend
npm run build
netlify deploy --prod
```

#### Backend (Render):
1. Go to render.com
2. New Web Service
3. Connect repo
4. Deploy

### Option 3: Single Server (DigitalOcean/AWS)

```bash
# On server
git clone your-repo
cd AI_Medicinal_Plant_Detection

# Use Docker
cd infrastructure/docker
docker-compose up -d

# Access via server IP
http://YOUR_SERVER_IP:3000
```

---

## Testing Checklist

### Functionality Tests

#### Backend API
- [ ] Health endpoint responds
- [ ] Plants list loads (6 plants)
- [ ] Plant details show correctly
- [ ] Image upload accepts files
- [ ] Predictions return results
- [ ] Confidence scores display
- [ ] Recommendations work
- [ ] Error handling works

#### Frontend
- [ ] Pages load without errors
- [ ] Navigation works
- [ ] Forms submit correctly
- [ ] Images upload successfully
- [ ] Results display properly
- [ ] Responsive on mobile
- [ ] Loading states show
- [ ] Error messages display

### UI/UX Tests

#### Desktop (1920x1080)
- [ ] Layout looks good
- [ ] Text readable
- [ ] Images sized correctly
- [ ] Buttons clickable
- [ ] Smooth animations

#### Tablet (768x1024)
- [ ] Responsive layout
- [ ] Touch targets large enough
- [ ] No horizontal scroll
- [ ] Images scale properly

#### Mobile (375x667)
- [ ] Single column layout
- [ ] Easy to tap buttons
- [ ] Text readable
- [ ] Upload works
- [ ] Results fit screen

### Performance Tests
- [ ] Page load < 3 seconds
- [ ] Prediction < 2 seconds
- [ ] Images load quickly
- [ ] No lag on interactions
- [ ] Smooth scrolling

---

## Quick Test Script

Save as `test_system.ps1`:

```powershell
Write-Host "🧪 Testing AI Medicinal Plant Detection System" -ForegroundColor Cyan

# Test Backend
Write-Host "`n1. Testing Backend..." -ForegroundColor Yellow
$health = curl http://localhost:8000/health 2>$null
if ($health) {
    Write-Host "✓ Backend is running" -ForegroundColor Green
} else {
    Write-Host "✗ Backend not responding" -ForegroundColor Red
}

# Test Plants API
Write-Host "`n2. Testing Plants API..." -ForegroundColor Yellow
$plants = curl http://localhost:8000/api/v1/plants/ 2>$null | ConvertFrom-Json
if ($plants.total -gt 0) {
    Write-Host "✓ Found $($plants.total) plants in database" -ForegroundColor Green
} else {
    Write-Host "✗ No plants found" -ForegroundColor Red
}

# Test Frontend
Write-Host "`n3. Testing Frontend..." -ForegroundColor Yellow
$frontend = curl http://localhost:3000 2>$null
if ($frontend) {
    Write-Host "✓ Frontend is running" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend not responding" -ForegroundColor Red
}

Write-Host "`n✅ Testing Complete!" -ForegroundColor Cyan
Write-Host "Access: http://localhost:3000" -ForegroundColor White
```

Run: `.\test_system.ps1`

---

## Mobile APK Build (Detailed)

### Using Expo EAS

1. **Install EAS CLI:**
```bash
npm install -g eas-cli
```

2. **Login:**
```bash
eas login
```

3. **Configure:**
```bash
cd mobile
eas build:configure
```

4. **Build APK:**
```bash
eas build --platform android --profile preview
```

5. **Download & Install:**
- Get APK from Expo dashboard
- Transfer to phone
- Install (enable "Unknown Sources")

### Using Capacitor (Alternative)

1. **Add Capacitor:**
```bash
cd frontend
npm install @capacitor/core @capacitor/cli
npx cap init
```

2. **Add Android:**
```bash
npm install @capacitor/android
npx cap add android
```

3. **Build:**
```bash
npm run build
npx cap copy
npx cap open android
```

4. **In Android Studio:**
- Build → Generate Signed Bundle/APK
- Choose APK
- Sign and build

---

## Browser Testing Tools

### Chrome DevTools
1. F12 → Toggle Device Toolbar
2. Test different screen sizes
3. Network tab → Check API calls
4. Console → Check for errors

### Lighthouse Audit
1. F12 → Lighthouse tab
2. Run audit
3. Check Performance, Accessibility, SEO

### Mobile Testing
- Chrome → Remote Debugging
- Connect phone via USB
- chrome://inspect

---

## Current System Status

**Ready for Testing:**
- ✅ Backend API (all endpoints)
- ✅ Frontend web app
- ✅ Database with 6 plants
- ✅ Mock ML predictions
- ✅ Responsive design

**To Build APK:**
1. Create React Native app (30 min)
2. Configure API endpoints
3. Build with Expo (15 min)
4. Test on device

**Or Use PWA:**
1. Add PWA support (10 min)
2. Test on mobile browser
3. Add to home screen
4. Works like native app!

---

## Support

For issues during testing:
- Check browser console (F12)
- Check backend logs
- Verify API URLs are correct
- Ensure ports 3000 and 8000 are open
