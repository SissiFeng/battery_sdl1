# SDL1 Backend Quick Reference Card

## 🚀 Essential Commands

### Start Backend Server
```bash
python src/api_server.py
# Server runs on: http://localhost:8000
```

### Health Check
```bash
curl http://localhost:8000/
```

### Check Available Managers
```bash
curl http://localhost:8000/managers
```

## 🔄 Manager Configuration

### Use Native Manager (Default)
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "native", "dry_run": true}'
```

### Use Prefect Manager (Advanced)
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "prefect", "dry_run": true}'
```

## 🧪 Workflow Testing

### Validate Canvas JSON
```bash
curl -X POST "http://localhost:8000/canvas/validate" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### Execute Workflow (Dry Run)
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### Execute Workflow (Live)
```bash
curl -X POST "http://localhost:8000/canvas/execute" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

## 🔍 Status & Monitoring

### Robot Status
```bash
curl http://localhost:8000/status
```

### View Logs
```bash
tail -f opentrons_api_$(date +%Y%m%d).log
```

### Check Errors
```bash
grep -i error opentrons_api_$(date +%Y%m%d).log
```

## 🎛️ Prefect Commands (Optional)

### Install Prefect
```bash
pip install prefect>=2.10.0 prefect-shell>=0.1.0
```

### Start Prefect Server
```bash
python src/prefect_cli.py server
# Web UI: http://127.0.0.1:4200
```

### Deploy Workflow
```bash
python src/prefect_cli.py deploy \
  data/test_workflow-1753364156528.json \
  "My Workflow"
```

### List Deployments
```bash
python src/prefect_cli.py list-deployments
```

### Compare Managers
```bash
python src/prefect_cli.py compare
```

## 🚨 Emergency Commands

### Stop Server
```bash
pkill -f api_server
```

### Force Kill
```bash
pkill -9 -f api_server
```

### Check Processes
```bash
ps aux | grep -E "(api_server|python)"
```

## 📊 Common API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| GET | `/managers` | List available managers |
| POST | `/managers/configure` | Configure manager |
| GET | `/status` | Robot status |
| POST | `/canvas/validate` | Validate workflow |
| POST | `/canvas/execute/dry-run` | Test execution |
| POST | `/canvas/execute` | Live execution |

## 🔧 Troubleshooting Quick Fixes

### Server Won't Start
```bash
pip install -r requirements.txt
python -c "from src.api_server import app; print('OK')"
```

### Robot Connection Issues
```bash
ping 169.254.69.185
# Use dry_run: true in configuration
```

### Prefect Not Available
```bash
pip install prefect>=2.10.0 prefect-shell>=0.1.0
python -c "import prefect; print('OK')"
```

### Workflow Fails
1. Check JSON format
2. Use dry-run first
3. Check server logs
4. Verify parameters

## 📁 Important Files

- `src/api_server.py` - Main server
- `data/test_workflow-1753364156528.json` - Test workflow
- `requirements.txt` - Dependencies
- `TESTING_MANUAL.md` - Full testing guide
- `docs/PREFECT_WORKFLOW_GUIDE.md` - Prefect guide

## 🎯 Daily Workflow

1. **Start**: `python src/api_server.py`
2. **Configure**: Choose manager type
3. **Validate**: Test workflow JSON
4. **Dry-run**: Test execution
5. **Execute**: Run live workflow
6. **Monitor**: Check logs and status

---
**For detailed instructions, see TESTING_MANUAL.md**
