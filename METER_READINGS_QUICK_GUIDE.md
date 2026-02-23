# Quick Reference: Meter Readings Feature

## For Admins

### Access the Dashboard
- Navigate to: **Bills > Meter Readings** in sidebar
- Or go to: `http://your-domain/meter-readings/`

### Add a New Meter Reading
1. Click the **+ (Add)** button on any customer row
2. Enter the **Current Reading** from the meter
3. Click **Save Reading**
4. System auto-calculates: Consumption = Current - Previous
5. Bill is generated automatically: Bill = Consumption × 200 KES

### View Customer's Reading History
1. Click the **⏱ (History)** button on a customer row
2. See all past readings in reverse chronological order
3. Click **Edit** to modify any specific reading

### Edit an Existing Reading
- From dashboard: Click **✎ (Edit)** button
- From history: Click **Edit** on any reading

### Search for a Customer
Use the search box to find by:
- Customer name
- Meter number
- Phone number

### Filter by Status
Select from dropdown:
- All Status
- Connected
- Disconnected
- Pending

## What Gets Calculated Automatically

| Formula | Example |
|---------|---------|
| Consumption = Current - Previous | 350 - 320 = 30 cu.m |
| Bill = Consumption × 200 | 30 × 200 = 6,000 KES |
| Penalty = Days Overdue × 5 | 10 days × 5 = 50 KES |
| Total = Bill + Penalty | 6,000 + 50 = 6,050 KES |

## Important Fields

| Field | Description | Required |
|-------|-------------|----------|
| Customer | Select from existing customers | Yes |
| Previous Reading | Last recorded reading (auto-filled) | Yes |
| Current Reading | Today's meter reading | Yes |
| Consumption | Auto-calculated (Current - Previous) | No (auto) |
| Billing Date | Date of this bill cycle | Yes |
| Due Date | Payment deadline | Yes |
| Penalty Date | Date penalties start accruing | Yes |
| Payment Status | Pending or Paid | Yes |
| Approval Status | Pending Approval or Approved | Yes |

## Actions Available

| Button | Action | Location |
|--------|--------|----------|
| + | Add new meter reading | Dashboard row |
| ⏱ | View reading history | Dashboard row |
| ✎ | Edit reading | Dashboard row / History |
| 🔍 | Filter/Search | Dashboard top |

## Status Badges

| Status | Color | Meaning |
|--------|-------|---------|
| Connected | Green | Customer meter is active |
| Disconnected | Red | Customer meter is inactive |
| Pending | Yellow | Awaiting connection |
| Paid | Green | Bill payment received |
| Pending | Yellow | Awaiting payment |
| Approved | Green | Bill approved by admin |
| Pending Approval | Yellow | Awaiting admin approval |
| Rejected | Red | Bill rejected |

## Typical Monthly Workflow

1. **Beginning of month:** Gather all meter readings
2. **Dashboard:** Add each customer's current reading
3. **System:** Automatically generates bills with calculations
4. **Approve Bills:** Review and approve pending bills
5. **Notify:** SMS notifications sent to customers
6. **Collect:** Monitor payments (go to "Ongoing Bills")

## Common Tasks

### Task: Find a customer's total consumption
→ Click **⏱ History** to see all readings and consumption

### Task: Correct a wrong reading
→ Click **✎ Edit** to modify the reading

### Task: See outstanding bills
→ Go to **Bills > Ongoing Bills**

### Task: Change billing rate
→ Admin settings (Metrics)

## Tips

- ✓ Use **Filter by Status** to quickly find connected customers
- ✓ **Search** is helpful if you have many customers
- ✓ Click **⏱ History** to verify consumption is reasonable
- ✓ Always set correct **Due Date** and **Penalty Date**
- ✓ Check **Payment Status** before adding a new reading

