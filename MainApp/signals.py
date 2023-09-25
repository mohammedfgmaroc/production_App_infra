from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Check if the groups already exist
    admin_group, created = Group.objects.get_or_create(name='Admin')
    technician_group, created = Group.objects.get_or_create(name='Technician')
    
    if created:
        print("Admin and Technician groups created.")
    else:
        print("Admin and Technician groups already exist.")
@receiver(post_save, sender=User)
def assign_superuser_to_group(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        group = Group.objects.get(name='Admin')  # Change the group name as needed
        instance.groups.add(group)