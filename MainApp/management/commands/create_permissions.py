from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create and assign permissions'

    def handle(self, *args, **options):
        # Get the content type for the Group model
        content_type = ContentType.objects.get_for_model(Group)

         # Create permissions
        can_access_upload = Permission.objects.create(codename='can_access_upload', name='Can access Upload page', content_type=content_type)
        can_access_data_visualization = Permission.objects.create(codename='can_access_data_visualization', name='Can access Data Visualization page', content_type=content_type)
        can_access_employee_management = Permission.objects.create(codename='can_access_employee_management', name='Can access Employee Management page', content_type=content_type)
        can_access_validation = Permission.objects.create(codename='can_access_validation', name='Can access Validation page', content_type=content_type)

        # Assign permissions to groups
        admin_group = Group.objects.get(name='Admin')
        technician_group = Group.objects.get(name='Technician')

        admin_group.permissions.add(can_access_upload)
        admin_group.permissions.add(can_access_data_visualization)
        admin_group.permissions.add(can_access_employee_management)
        admin_group.permissions.add(can_access_validation)

        technician_group.permissions.add(can_access_upload)
        technician_group.permissions.add(can_access_data_visualization)

        self.stdout.write(self.style.SUCCESS('Permissions created and assigned successfully.'))
