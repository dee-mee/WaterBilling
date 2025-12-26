from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='deemvee').exists():
    User.objects.create_superuser('deemvee', 'deemee@example.com', 'Settings4$')
