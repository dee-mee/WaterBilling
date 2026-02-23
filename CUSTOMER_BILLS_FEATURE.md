# Customer Bill Viewing & Receipt Download Feature

## Overview

Customers can now view their billing history and download PDF receipts from their account dashboard. This is a **read-only** view - customers can see their bills but cannot modify any information.

## Features

### 1. Customer Bills Dashboard
**URL:** `/my-bills/`
**Access:** Login required (customers only)

**Displays:**
- Meter number (reference)
- Connection status (Connected/Disconnected/Pending)
- Total number of bills

**Table Shows:**
- **Month** - Billing period (e.g., "February 2026")
- **Previous Reading** - Last month's meter reading
- **Current Reading** - This month's meter reading
- **Consumption** - Water used (Current - Previous)
- **Bill Amount** - Consumption × 200 KES
- **Penalty** - Late charges (if applicable)
- **Total Due** - Bill + Penalty
- **Payment Status** - Paid or Pending Payment
- **Due Date** - Payment deadline
- **Action** - Download receipt button

### 2. Receipt Download
**Format:** PDF document
**Contents:**
- Water Billing System header
- Customer information (name, meter number, address)
- Bill details (readings, consumption, amounts)
- Payment information (due date, payment status)
- Billing period

### 3. Customer Information Card
Shows:
- Meter Number
- Connection Status
- Total Bills count

### 4. Billing Information Guide
Displays in the bill view:
- How to read each bill component
- What consumption means
- Payment due dates and penalties
- How penalties are calculated

## How Customers Use It

### Step 1: Login to Account
- Customer logs in with email and password
- OTP verification (if enabled)

### Step 2: Navigate to Bills
- Click: **My Bills** in the sidebar (new!)
- Or click: **Bills** menu if available
- See dashboard with all bills

### Step 3: View Bills
- See all billing history in table
- Each row shows one month's bill
- Latest bills shown first
- Sort by any column
- Search bills

### Step 4: Check Status
- **Paid** badges show paid bills (green)
- **Pending Payment** badges show unpaid bills (yellow)
- View amount due and due date

### Step 5: Download Receipt
- Click **[📥 Receipt]** button on any bill
- PDF downloads to computer
- Rename if needed
- Print or share as needed

## Bill Components Explained

### What Customers See

| Item | Explanation | Example |
|------|-------------|---------|
| Month | Billing period | February 2026 |
| Previous Reading | Last month's reading | 1,000 cu.m |
| Current Reading | This month's reading | 1,050 cu.m |
| Consumption | Water used (current - previous) | 50 cu.m |
| Bill Amount | Cost of water (consumption × 200 KES) | 10,000 KES |
| Penalty | Late charge (5 KES per day) | 50 KES |
| Total Due | Bill + Penalty | 10,050 KES |
| Payment Status | Paid or Pending | Pending Payment |
| Due Date | By when to pay | March 10, 2026 |

### Calculation Explanation

**How is my bill calculated?**

```
Water Used = Current Meter Reading - Previous Meter Reading
           = 1,050 - 1,000
           = 50 cubic meters

Bill Amount = Water Used × 200 KES
            = 50 × 200
            = 10,000 KES

If Paid After Due Date:
Penalty = Number of Days Late × 5 KES
        = 10 days × 5
        = 50 KES

Total Due = Bill Amount + Penalty
          = 10,000 + 50
          = 10,050 KES
```

## Receipt PDF Details

### What's Included

1. **Company Header**
   - Water Billing System logo
   - Title and date

2. **Customer Information**
   - Full name
   - Meter number
   - Address

3. **Bill Details**
   - Billing period
   - Due date
   - Meter readings (previous & current)
   - Water consumption
   - Total bill amount
   - Payment status

4. **Footer**
   - Receipt ID
   - Generation date
   - Contact information

### How to Use Receipt

- **Keep for records** - Store in safe place
- **Proof of bill** - Shows what you were charged
- **Dispute reference** - Use to reference a specific bill
- **Payment proof** - Attach when paying online
- **Print** - Can print for physical records

## Navigation

### Customer Sidebar Menu
```
My Account
├── My Meter (view consumption graph)
├── My Bills (view billing history) ← NEW!
├── Notifications
├── Support
└── Settings
```

### Access Points
- **Main Link:** My Bills in sidebar
- **Direct URL:** `/my-bills/`
- **Menu:** My Bills dropdown

## Data Visible vs Hidden

### Customers CAN See
✓ Their meter number
✓ Their connection status
✓ All their approved bills
✓ Consumption readings
✓ Bill amounts
✓ Payment status
✓ Due dates
✓ Penalty information

### Customers CANNOT See
✗ Other customers' information
✗ Edit/modify any bill information
✗ Admin-only features
✗ Payment transaction details
✗ Invoice history dates
✗ Approval/rejection reasons

### Customers CANNOT Do
✗ Edit bills
✗ Delete bills
✗ Change payment status
✗ Modify readings
✗ Access admin dashboard
✗ See other customers' data

## Security Features

✓ **Login Required** - Only authenticated users can view
✓ **Customer-Specific** - Each customer sees only their own bills
✓ **Approved Bills Only** - Only admin-approved bills visible
✓ **Read-Only Access** - No modification possible
✓ **PDF Security** - Downloads as file, no inline viewer exploits
✓ **Session Protection** - Django session security

## Technical Details

### Database Query
```python
bills = WaterBill.objects.filter(
    name=client,
    approval_status='Approved'  # Only approved bills
).order_by('-billing_date')  # Newest first
```

### Customer View Restrictions
- Only sees bills for their own meter
- Cannot see bills in "Pending Approval" status
- Cannot see rejected bills
- Cannot access admin bill management
- Cannot download receipts for other customers

## Receipt Download Workflow

1. **Customer clicks Receipt button**
   ↓
2. **System verifies:**
   - Customer is logged in
   - Bill belongs to customer
   - Bill is approved
   ↓
3. **System generates PDF:**
   - Retrieves bill data
   - Creates PDF document
   - Adds customer information
   - Adds bill details
   - Calculates totals
   ↓
4. **System sends download:**
   - Sets proper headers
   - Sends as attachment
   - Browser shows "Save As" dialog
   ↓
5. **Customer saves file**
   - Chooses download location
   - Renames if desired
   - File saved locally

## Responsive Design

- ✓ Desktop computer - Full table view
- ✓ Tablet - Responsive columns hide on smaller screens
- ✓ Mobile phone - Touch-friendly buttons, stack view
- ✓ All devices - Download button always visible

## Common Customer Questions

**Q: Why can't I edit my bill?**
A: Bills are set by administrators to prevent fraud. If there's an error, contact support.

**Q: How do I view old bills?**
A: All your bills are shown in the table. Scroll down or search to find older ones.

**Q: Can I download all receipts at once?**
A: Currently you download one at a time. Contact support for bulk downloads.

**Q: What if my receipt doesn't download?**
A: Check your browser's download settings and firewall. Try a different browser if issues persist.

**Q: How long are receipts kept?**
A: All billing history is kept permanently in the system.

**Q: Can I pay from this page?**
A: Payment links are available in the "Ongoing Bills" section. Check that page for payment options.

## Features Coming Soon (Optional)

- [ ] Payment history from this view
- [ ] Email receipts automatically
- [ ] Download multiple receipts
- [ ] Email reminder when bill is due
- [ ] Consumption graph
- [ ] Comparison with previous months
- [ ] Export to CSV
- [ ] Mobile app access

## Navigation Summary

| Page | URL | Access | Purpose |
|------|-----|--------|---------|
| My Meter | `/my-meter/` | Customer | View meter readings & consumption graph |
| My Bills | `/my-bills/` | Customer | View bills & download receipts (NEW!) |
| Ongoing Bills | `/bills/ongoing/` | Both | Pay bills (customers), manage bills (admin) |
| Settings | `/settings/` | Customer | Update profile |

---

## Files Created/Modified

**New Template:**
- `main/templates/main/customer_bills.html`

**New View Function:**
- `customer_bills_view()` in `main/views.py`

**Modified Files:**
- `main/urls.py` - Added `/my-bills/` route
- `main/templates/main/layout.html` - Added navigation link

**Existing Functionality Used:**
- `download_invoice()` - Generates PDF receipts

## System Integration

### Works With
- ✓ Existing payment system
- ✓ Existing bill approval workflow
- ✓ Existing SMS notifications
- ✓ Existing customer authentication
- ✓ Existing PDF invoice generation

### Dependencies
- Django 3.x or higher
- ReportLab (already installed)
- Bootstrap CSS (already included)
- Font Awesome icons (already included)

---

**Status:** ✅ Ready to Deploy

**Last Updated:** 2026-02-23

