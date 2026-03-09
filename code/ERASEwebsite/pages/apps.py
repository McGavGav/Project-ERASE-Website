from django.apps import AppConfig

class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages'

    def ready(self):
        from django.contrib.auth.models import Group, Permission

        # Create groups if they don't exist
        admin_group, created = Group.objects.get_or_create(name='admin')
        user_group, created = Group.objects.get_or_create(name='normal users')

        # perms for admins
        if created:
            admin_permissions = Permission.objects.all()
            admin_group.permissions.set(admin_permissions)

        #set normal user perms here.
