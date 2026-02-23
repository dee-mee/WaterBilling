# Demo Credentials - Water Billing System

## 🔐 Test Accounts for Render Deployment

Use these credentials to test the system after deployment on Render:

### Admin Account
```
Email:    admin@example.com
Password: 12345678
```
**Access Level:** Full admin privileges - can add meter readings, approve bills, manage customers

**Admin Features:**
- Dashboard: Bills → Meter Readings
- Add/edit meter readings for all customers
- View consumption and bill calculations
- Approve pending bills
- Generate reports

---

### Customer Account
```
Email:    user1@gmail.com
Password: password
```
**Access Level:** Customer - read-only access to own bills

**Customer Features:**
- View personal billing history
- Download PDF receipts
- See meter readings (month, previous/current readings, consumption, bill amount)
- View payment status and due dates

---

## 🚀 How to Test After Deployment

### 1. Login as Admin
1. Navigate to: `https://your-app-name.onrender.com/`
2. Click **"Login"** → **"Admin Login"**
3. Enter admin credentials above
4. You'll see the admin dashboard

### 2. Test Admin Features
- Go to **Bills** → **Meter Readings**
- Search/filter customers
- Click **Add Reading** for a customer
- Enter meter readings (auto-calculates consumption and bill)
- Verify bill = consumption × 200 KES ✓

### 3. Login as Customer
1. Logout from admin account
2. Click **"Login"** → **"Customer Login"**
3. Enter customer credentials above
4. Click **"My Bills"** in sidebar
5. View your billing history
6. Download any receipt as PDF

### 4. Verify Billing Calculation
- Expected formula: **Bill = Consumption × 200 KES**
- Example: If consumption = 50 cu.m, bill should = 10,000 KES
- Check this is working correctly ✓

---

## 📋 Billing Formula Reference

| Component | Formula | Example |
|-----------|---------|---------|
| Consumption | Current Reading - Previous Reading | 1,050 - 1,000 = 50 |
| Base Bill | Consumption × 200 KES | 50 × 200 = 10,000 KES |
| Penalty (if overdue) | Days Late × 5 KES | 30 days × 5 = 150 KES |
| **Total Payable** | **Base Bill + Penalty** | **10,000 + 150 = 10,150 KES** |

---

## ⚠️ Important Notes

- **DO NOT** use these credentials for production (public) deployment
- **DO** change these credentials before going live with real customers
- **DO** create separate test and production credentials
- These are for **testing purposes only**

---

## 🔄 Creating Additional Test Accounts

If you need more test customers, use the Admin Dashboard:

1. Login as admin
2. Go to **Admin Panel** → **Clients**
3. Click **Add Client**
4. Fill in customer details
5. Create associated account
6. Add meter readings to generate bills

---

## 📞 Database Setup

The system uses an SQLite database with pre-configured demo data:
- Admin account already created ✓
- Customer account already created ✓
- Sample meter readings available ✓
- Bills auto-generated based on readings ✓

**No additional database setup needed!**

---

**Last Updated:** February 23, 2026
