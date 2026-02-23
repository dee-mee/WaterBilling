# Admin Meter Readings Dashboard - Feature Documentation

## Overview

The **Meter Readings Dashboard** is a new admin-only feature that provides a centralized interface for managing customer meter readings and generating water bills. This feature streamlines the process of tracking consumption data and calculating bills.

## Key Features

### 1. **Meter Readings Dashboard**
**URL:** `/meter-readings/`

A comprehensive table view showing all customers with their latest meter readings:

**Columns:**
- **Meter Number** - Unique identifier for the meter
- **Customer Name** - Full name (Last Name, First Name)
- **Status** - Connection status (Connected/Disconnected/Pending)
- **Month** - Billing month in format "Month Year"
- **Previous Reading** - Reading from previous billing period
- **Current Reading** - Latest meter reading
- **Consumption (cu.m)** - Calculated: Current Reading - Previous Reading
- **Bill (KES)** - Calculated: Consumption × 200
- **Payment Status** - Paid/Pending
- **Actions** - Quick buttons to add readings, view history, or edit

**Features:**
- Search by customer name, meter number, or phone
- Filter by connection status
- Sort by any column
- Responsive table design
- Quick action buttons for each customer

### 2. **Add Meter Reading**
**URL:** `/meter-readings/add/<client_id>`

Form to enter new meter readings for a specific customer.

**Fields:**
- Customer (pre-selected)
- Previous Reading (auto-filled from last reading)
- Current Reading (manual entry)
- Meter Consumption (auto-calculated)
- Billing Date
- Payment Status
- Due Date
- Penalty Date
- Approval Status

**Features:**
- Auto-calculation: `Consumption = Current Reading - Previous Reading`
- Helpful sidebar showing billing formula
- Real-time validation
- Success/error notifications

### 3. **Reading History**
**URL:** `/meter-readings/history/<client_id>`

Complete historical view of all meter readings for a customer.

**Display:**
- Chronologically sorted readings (newest first)
- All columns: Month, Previous Reading, Current Reading, Consumption, Bill Amount
- Payment and Approval Status for each bill
- Quick edit access for any reading

**Metrics:**
- Total readings count
- Paid bills count

## Billing Formula

The system uses the following calculation:

```
Consumption (cu.m) = Current Reading - Previous Reading
Bill Amount (KES) = Consumption × 200
Total Payable = Bill Amount + Penalty (if applicable)

Penalty = (Days Overdue) × 5 KES
  (Calculated after Penalty Date)
```

## User Workflow

### Admin Steps to Create a Bill:

1. Go to **Bills > Meter Readings** in the sidebar
2. Find the customer in the dashboard table
3. Click the **+** (Add) button
4. Enter the current meter reading
5. System automatically calculates consumption
6. Review the bill amount and dates
7. Click "Save Reading"
8. Bill is created and ready for approval

### Managing Readings:

- **Edit a Reading:** Click the ✎ (Edit) button or go to the reading history
- **View History:** Click the ⏱ (History) button to see all readings for a customer
- **Filter Readings:** Use search box or status filter on dashboard

## Important Notes

- **Auto-calculation:** Consumption is automatically calculated; manual entry is only needed for corrections
- **Rate Configuration:** The rate (200 KES per cu.m) can be changed in the Metrics settings
- **Approval Workflow:** Bills can be created as "Pending Approval" or "Approved"
- **SMS Integration:** When a bill is added, SMS notifications are automatically sent to customers (if configured)

## Navigation

The Meter Readings Dashboard is accessible from:
- Admin Dashboard
- Main Navigation: **Bills > Meter Readings**
- Direct URL: `/meter-readings/`

## Technical Details

### Database Tables Used:
- `Client` - Customer information (meter_number, contact_number, status)
- `WaterBill` - Billing records (readings, consumption, amounts, dates)
- `Metric` - Billing rates (consump_amount, penalty_amount)

### Related Views:
- `meter_readings_dashboard` - Main dashboard
- `add_meter_reading` - Add new reading form
- `customer_reading_history` - View customer history
- `update_bills` - Edit existing bill (from ongoing bills)

### Related URLs:
```
/meter-readings/ - Dashboard
/meter-readings/add/<client_id> - Add reading
/meter-readings/history/<client_id> - View history
```

## Security

- Admin-only access (requires `is_superuser` flag)
- CSRF protection on all forms
- Input validation on numeric fields
- No customer data exposure

## Improvements Made

1. **Better Organization:** Separate dedicated interface for meter readings
2. **Cleaner UX:** Dedicated forms instead of modal popups
3. **Auto-calculations:** Real-time consumption calculations
4. **History Tracking:** Easy access to reading history
5. **Quick Actions:** Fast navigation between related views
6. **Search & Filter:** Quickly find customers
7. **Mobile Responsive:** Works on all device sizes

