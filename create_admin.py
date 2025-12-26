from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='deemee').exists():
    User.objects.create_superuser('deemee', 'deemee@gmail.com', 'Settings4$')
