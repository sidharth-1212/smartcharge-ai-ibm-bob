# ⚡ SmartCharge AI - Quick Start (3 Commands)

## 🎯 Fastest Way to Start

### 1️⃣ Add Your IBM Bob API Key
```bash
# Edit .env in project root
IBM_BOB_API_KEY=your_actual_key_here
```

### 2️⃣ Start Everything
```bash
# Terminal 1 - Infrastructure
docker-compose up -d postgres redis

# Terminal 2 - Backend
cd backend && .\venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 - Simulator (already running! ✓)
cd simulator && python simulator.py

# Terminal 4 - Frontend
cd frontend && npm run dev
```

### 3️⃣ Open Dashboard
```
http://localhost:3000
```

## ✅ Success Check

You should see:
- ✅ Simulator: "API: ✓" (instead of ✗)
- ✅ Backend: "Application startup complete"
- ✅ Frontend: Dashboard with live gauges
- ✅ Bob's decisions appearing every 5 seconds

## 🚨 Current Status

**Simulator:** ✅ RUNNING (Terminal 1)
- Generating telemetry every 5 seconds
- Waiting for backend to connect

**Backend:** ❌ NOT STARTED
- Need to start in new terminal

**Frontend:** ❌ NOT STARTED
- Need to start in new terminal

## 📝 Next Steps

1. **Keep simulator running** (it's working!)
2. **Open new terminal** → Start backend
3. **Open another terminal** → Start frontend
4. **Watch the magic happen!** 🎉

---

**See STARTUP_GUIDE.md for detailed instructions and troubleshooting**