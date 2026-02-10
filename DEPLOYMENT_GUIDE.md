# 🚀 COMPLETE DEPLOYMENT GUIDE
# Spa/Salon Agentic System - Cloud Deployment

## 📋 Prerequisites

✅ Supabase account (https://supabase.com)
✅ Fly.io account (https://fly.io)
✅ Anthropic API key (https://console.anthropic.com)
✅ Git installed locally
✅ Fly CLI installed (https://fly.io/docs/hands-on/install-flyctl/)

---

## PART 1: SUPABASE SETUP (5 minutes)

### Step 1: Create Supabase Project

1. **Go to** https://supabase.com/dashboard
2. **Click** "New Project"
3. **Fill in:**
   - Name: `spa-agentic-system`
   - Database Password: (create a strong password - SAVE THIS!)
   - Region: Choose closest to you
4. **Click** "Create new project"
5. **Wait** ~2 minutes for provisioning

### Step 2: Get Database Connection Details

1. **Click** "Project Settings" (⚙️ icon)
2. **Click** "Database" in sidebar
3. **Find "Connection string"** section
4. **Copy** these values:
   ```
   Host: db.xxxxx.supabase.co
   Port: 5432
   Database: postgres
   User: postgres
   Password: [your password from Step 1]
   ```

### Step 3: Run Database Schema

1. **In Supabase Dashboard**, click "SQL Editor"
2. **Click** "New query"
3. **Open** `deployment/supabase_schema.sql` from this project
4. **Copy the ENTIRE file** into the editor
5. **Click** "Run" (or press Ctrl/Cmd + Enter)
6. **Wait** ~10 seconds
7. **You should see:** "Success. No rows returned"

### Step 4: Verify Database

1. **Click** "Table Editor" in sidebar
2. **You should see tables:**
   - customers
   - appointments
   - staff
   - services
   - sales
   - retail_products
   - agent_actions
   - agent_memory

3. **Click** `staff` table
4. **You should see 4 staff members** (Sarah, Michael, Jessica, Emily)

✅ **Supabase is ready!**

---

## PART 2: FLY.IO SETUP (10 minutes)

### Step 1: Install Fly CLI

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Verify installation:**
```bash
fly version
```

### Step 2: Login to Fly.io

```bash
fly auth login
```

This opens a browser for authentication.

### Step 3: Create Fly App

```bash
cd spa-cloud
fly launch
```

**When prompted:**

```
? Choose an app name (leave blank to generate one): spa-agentic-system
? Choose a region: (select closest to you)
? Would you like to set up a Postgresql database? No
? Would you like to set up an Upstash Redis database? No
? Would you like to deploy now? No
```

### Step 4: Set Environment Variables

**Set your secrets:**

```bash
# Database from Supabase
fly secrets set DB_HOST=db.xxxxx.supabase.co
fly secrets set DB_PORT=5432
fly secrets set DB_NAME=postgres
fly secrets set DB_USER=postgres
fly secrets set DB_PASSWORD=your_supabase_password

# Anthropic API key
fly secrets set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Replace:**
- `db.xxxxx.supabase.co` with your actual Supabase host
- `your_supabase_password` with your actual password
- `sk-ant-your-key-here` with your actual Anthropic key

### Step 5: Deploy!

```bash
fly deploy
```

**This will:**
- Build Docker image
- Push to Fly.io
- Deploy your app
- Takes ~3-5 minutes

**When complete, you'll see:**
```
Visit your newly deployed app at https://spa-agentic-system.fly.dev
```

### Step 6: Verify Deployment

**Check app status:**
```bash
fly status
```

**View logs:**
```bash
fly logs
```

**Open in browser:**
```bash
fly open
```

Or visit: `https://spa-agentic-system.fly.dev`

You should see:
```json
{
  "status": "healthy",
  "service": "Spa/Salon Agentic System",
  "version": "1.0.0"
}
```

✅ **Fly.io deployment complete!**

---

## PART 3: TEST YOUR DEPLOYMENT

### Test 1: Dashboard

Visit: `https://spa-agentic-system.fly.dev/dashboard`

You should see the beautiful dashboard with:
- Today's overview
- Staff status
- AI Agent activity
- Reports

### Test 2: API Endpoints

**Get customers:**
```bash
curl https://spa-agentic-system.fly.dev/api/customers
```

**Get staff:**
```bash
curl https://spa-agentic-system.fly.dev/api/staff
```

**Get services:**
```bash
curl https://spa-agentic-system.fly.dev/api/services
```

### Test 3: Run AI Analysis

**Visit dashboard and click:**
- 📈 Analyze Utilization
- ⚠️ Detect Churn Risk
- 🌅 Daily Business Analysis

**Watch AI agents work!**

---

## PART 4: POPULATE TEST DATA (Optional)

If you want realistic test data for demos:

### Option A: Use Supabase SQL Editor

1. **Create file:** `test_data.sql` with:

```sql
-- Create 20 sample customers
INSERT INTO customers (name, email, phone, first_visit, last_visit, total_visits, total_spent)
SELECT 
    'Customer ' || i,
    'customer' || i || '@example.com',
    '+1555000' || LPAD(i::TEXT, 4, '0'),
    CURRENT_DATE - (random() * 365)::INT,
    CURRENT_DATE - (random() * 60)::INT,
    (random() * 20)::INT + 1,
    (random() * 2000)::NUMERIC + 100
FROM generate_series(1, 20) i;

-- Create appointments for next 7 days
INSERT INTO appointments (customer_id, staff_id, scheduled_date, start_time, end_time, status, total_amount)
SELECT 
    (SELECT id FROM customers ORDER BY random() LIMIT 1),
    (SELECT id FROM staff ORDER BY random() LIMIT 1),
    CURRENT_DATE + (random() * 7)::INT,
    ('09:00'::TIME + (random() * INTERVAL '8 hours')),
    ('10:00'::TIME + (random() * INTERVAL '8 hours')),
    'scheduled',
    (random() * 200)::NUMERIC + 50
FROM generate_series(1, 50);
```

2. **Run in Supabase SQL Editor**

### Option B: Use API

```bash
# Create customers via API
curl -X POST https://spa-agentic-system.fly.dev/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+15551234567"
  }'
```

---

## 🎯 YOUR SYSTEM IS LIVE!

### What You Have:

✅ **Database:** Supabase PostgreSQL with full schema
✅ **Backend:** FastAPI running on Fly.io
✅ **AI Agents:** Scheduler and Client Intelligence active
✅ **Dashboard:** Web UI accessible anywhere
✅ **API:** RESTful endpoints for all operations

### URLs:

- **Dashboard:** https://spa-agentic-system.fly.dev/dashboard
- **API Docs:** https://spa-agentic-system.fly.dev/docs
- **Health:** https://spa-agentic-system.fly.dev/

### Sharing:

Share your dashboard URL with:
- CEO
- Investors
- Team members
- Clients

**No installation required - just open browser!**

---

## 🔧 COMMON COMMANDS

### View logs:
```bash
fly logs
```

### SSH into app:
```bash
fly ssh console
```

### Restart app:
```bash
fly apps restart spa-agentic-system
```

### Check status:
```bash
fly status
```

### Scale up (if needed):
```bash
fly scale vm shared-cpu-1x --memory 1024
```

### Update app:
```bash
# After making code changes
fly deploy
```

---

## 🐛 TROUBLESHOOTING

### App won't start:

**Check logs:**
```bash
fly logs
```

**Common issues:**
- Missing environment variables → Check `fly secrets list`
- Database connection → Verify Supabase host/password
- API key → Check Anthropic key is valid

### Database connection fails:

**Test connection from Fly.io:**
```bash
fly ssh console
python3
>>> import asyncpg
>>> import asyncio
>>> async def test():
...     conn = await asyncpg.connect(
...         host='db.xxxxx.supabase.co',
...         database='postgres',
...         user='postgres',
...         password='your_password'
...     )
...     print("Connected!")
...     await conn.close()
>>> asyncio.run(test())
```

### Dashboard not loading:

**Check:**
1. App is running: `fly status`
2. No errors in logs: `fly logs`
3. Try: `fly apps restart spa-agentic-system`

---

## 💰 COSTS

### Free Tier:

- **Supabase:** 500MB database, 2GB bandwidth (FREE)
- **Fly.io:** 3 shared VMs, 160GB bandwidth (FREE)
- **Anthropic:** Pay per use (~$0.03/analysis)

**Total monthly cost:** $0-10 for demo/testing

### Scaling:

If you need more:
- **Supabase Pro:** $25/month (8GB database)
- **Fly.io:** ~$5-15/month for production
- **Anthropic:** ~$30-50/month with regular use

---

## 🚀 NEXT STEPS

### For Demo:
1. ✅ Add more test data
2. ✅ Run daily analysis workflow
3. ✅ Show to stakeholders
4. ✅ Collect feedback

### For Production:
1. Add authentication (Supabase Auth)
2. Set up custom domain
3. Enable SSL/TLS
4. Add monitoring (Fly.io metrics)
5. Set up backups (Supabase automatic)

---

## 📞 SUPPORT

**Supabase Issues:**
- Docs: https://supabase.com/docs
- Support: https://supabase.com/support

**Fly.io Issues:**
- Docs: https://fly.io/docs
- Community: https://community.fly.io

**This System:**
- Check logs first: `fly logs`
- Review API docs: /docs endpoint
- Test endpoints individually

---

**🎉 Congratulations! Your cloud-native agentic system is LIVE!**

Share your dashboard URL and show the world what autonomous AI can do! 🚀
