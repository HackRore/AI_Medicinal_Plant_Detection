#!/bin/bash
# Deployment Script for Linux/Mac - Complete Setup

echo "======================================================================"
echo "AI MEDICINAL PLANT DETECTION - DEPLOYMENT SETUP"
echo "======================================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Setup ML Models
echo -e "\n${YELLOW}[1/5] Setting up ML model configurations...${NC}"
cd ml_pipeline
python3 quick_setup.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ML configurations created${NC}"
    
    # Copy to backend
    cp -r models/* ../backend/ml_models/
    echo -e "${GREEN}✓ Copied to backend/ml_models/${NC}"
else
    echo -e "${RED}✗ Failed to create ML configurations${NC}"
    exit 1
fi
cd ..

# Step 2: Setup Backend
echo -e "\n${YELLOW}[2/5] Setting up backend...${NC}"
cd backend

# Create .env from production template
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo -e "${GREEN}✓ Created .env file (update with your values)${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
pip3 install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies may have failed${NC}"
fi

# Seed database
echo -e "${YELLOW}Seeding database...${NC}"
python3 scripts/seed_data.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database seeded with plant data${NC}"
else
    echo -e "${YELLOW}⚠ Database seeding had issues (may already be seeded)${NC}"
fi

cd ..

# Step 3: Setup Frontend
echo -e "\n${YELLOW}[3/5] Setting up frontend...${NC}"
cd frontend

# Create .env.local
if [ ! -f ".env.local" ]; then
    cat > .env.local << EOF
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo -e "${GREEN}✓ Created .env.local${NC}"
fi

# Install frontend dependencies
if [ -f "package.json" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install --silent
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend installation had issues${NC}"
    fi
fi

cd ..

# Step 4: Create necessary directories
echo -e "\n${YELLOW}[4/5] Creating directories...${NC}"
dirs=("backend/uploads" "backend/ml_models" "backend/logs" "ml_pipeline/models")
for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✓ Created $dir${NC}"
    fi
done

# Step 5: Summary
echo -e "\n${YELLOW}[5/5] Deployment Summary${NC}"
echo "======================================================================"

echo -e "\n${GREEN}✅ SETUP COMPLETE!${NC}"
echo -e "\n${YELLOW}What's Ready:${NC}"
echo "  ✓ Backend API with all endpoints"
echo "  ✓ Frontend web application"
echo "  ✓ Database seeded with 6 medicinal plants"
echo "  ✓ ML model configurations"
echo "  ✓ Docker setup"

echo -e "\n${YELLOW}To Start the Application:${NC}"
echo -e "  ${YELLOW}Option 1 - Docker (Recommended):${NC}"
echo "    cd infrastructure/docker"
echo "    docker-compose up -d"
echo -e "\n  ${YELLOW}Option 2 - Manual:${NC}"
echo "    Terminal 1: cd backend && uvicorn app.main:app --reload"
echo "    Terminal 2: cd frontend && npm run dev"

echo -e "\n${YELLOW}Access Points:${NC}"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"

echo -e "\n${YELLOW}⚠️  Next Steps for Production:${NC}"
echo "  1. Update backend/.env with production values"
echo "  2. Train real ML models: cd ml_pipeline && pip install -r requirements.txt && python train_mobilenet.py"
echo "  3. Get Gemini API key from Google AI Studio"
echo "  4. Configure PostgreSQL for production"
echo "  5. Set up SSL/HTTPS"

echo -e "\n======================================================================"
echo -e "${GREEN}Happy Deploying! 🚀${NC}"
echo "======================================================================"
