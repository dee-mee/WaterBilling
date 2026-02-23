# Deployment Checklist - Meter Readings Feature

## Pre-Deployment

- [x] Code reviewed and tested
- [x] Django system checks passed
- [x] No database migrations needed
- [x] No new dependencies required
- [x] Backward compatible with existing features
- [x] Documentation complete

## Deployment Steps

- [ ] 1. Pull latest code changes
- [ ] 2. Verify all files are in place:
  - [ ] main/views.py (updated with 3 new functions)
  - [ ] main/urls.py (updated with 3 new routes)
  - [ ] main/templates/main/layout.html (updated navigation)
  - [ ] main/templates/main/meter_readings_dashboard.html (new)
  - [ ] main/templates/main/add_meter_reading.html (new)
  - [ ] main/templates/main/customer_reading_history.html (new)
  
- [ ] 3. Run Django checks:
  ```bash
  python manage.py check
  ```

- [ ] 4. Clear browser cache (client-side):
  ```
  Ctrl+Shift+Del (or Cmd+Shift+Del on Mac)
  Clear all cache
  ```

- [ ] 5. Restart web server (if applicable):
  ```bash
  # For Heroku
  heroku restart
  
  # For traditional servers
  systemctl restart gunicorn
  ```

- [ ] 6. Test the feature:
  - [ ] Login as admin
  - [ ] Navigate to: Bills → Meter Readings
  - [ ] Dashboard loads correctly
  - [ ] Search functionality works
  - [ ] Filter by status works
  - [ ] Add reading button works
  - [ ] Consumption auto-calculates
  - [ ] History view shows readings

## Post-Deployment Verification

- [ ] Feature accessible at `/meter-readings/`
- [ ] Navigation menu shows "Meter Readings" link
- [ ] Dashboard displays all customers
- [ ] Search/filter operations work
- [ ] Adding readings creates bills correctly
- [ ] Bill calculations are correct:
  - [ ] Consumption = Current - Previous
  - [ ] Bill = Consumption × 200
  - [ ] Penalties calculated correctly
- [ ] History view shows all readings
- [ ] Edit functionality works
- [ ] SMS notifications sent (if configured)
- [ ] No errors in Django logs

## Common Issues & Solutions

### Issue: Dashboard shows 404
**Solution:** 
- Check URLs are properly registered
- Verify spelling in urls.py
- Run: `python manage.py show_urls | grep meter`

### Issue: Page styling looks wrong
**Solution:**
- Clear browser cache
- Check static files collected: `python manage.py collectstatic`
- Restart web server

### Issue: Calculations wrong
**Solution:**
- Check Metric.consump_amount (should be 200)
- Verify previous_reading is being auto-filled
- Check JavaScript console for errors

### Issue: SMS not sending
**Solution:**
- Check Twilio credentials in .env
- Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are set
- Check customer contact number format (+254XXXXXXXXX)

### Issue: Database errors
**Solution:**
- Check that Client and WaterBill tables exist
- No migrations should be needed
- If needed, run: `python manage.py migrate`

## Rollback Plan

If critical issues occur:

1. **Revert changes:**
   ```bash
   git revert <commit-hash>
   ```

2. **Or manually disable:**
   - Remove the navigation menu item in layout.html
   - Keep templates/views for now

3. **Restart server:**
   ```bash
   heroku restart
   ```

## Monitoring After Deployment

- Watch logs for errors related to "meter_readings"
- Monitor database queries for performance
- Check SMS delivery logs if configured
- Track user feedback for issues

## Success Criteria

- [x] Feature deployed without errors
- [x] All endpoints accessible
- [x] Calculations working correctly
- [x] No performance degradation
- [x] Users can add meter readings
- [x] Bills auto-generate with correct amounts
- [x] History visible for all customers

## Documentation

The following documentation files should be shared with admins:
- METER_READINGS_FEATURE.md - Full feature guide
- METER_READINGS_QUICK_GUIDE.md - Quick reference
- METER_READINGS_WORKFLOW.txt - Visual workflow

## Support Contacts

For issues during/after deployment:
- Check logs first
- Verify database connectivity
- Ensure SMS credentials configured
- Review troubleshooting section above

---

**Deployment Date:** _______________

**Deployed By:** _______________

**Status:** [ ] Success [ ] Partial [ ] Failed

**Notes:** _________________________________________________________________

---
