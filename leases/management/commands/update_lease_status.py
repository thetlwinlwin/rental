from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from leases.models import Lease, LeaseStatus
from properties.models import AvailabilityStatus


class Command(BaseCommand):
    help = 'Checks for active leases whose end date has passed and updates their status to Completed, making the property available.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        self.stdout.write(f"[{timezone.now()}] Running update_lease_status command...")

        
        expired_leases = Lease.objects.filter(
            status=LeaseStatus.ACTIVE,
            end_date__lt=today
        ).select_related('property') 

        if not expired_leases.exists():
            self.stdout.write("No expired active leases found.")
            return

        completed_count = 0
        property_updated_count = 0

        
        try:
            with transaction.atomic():
                for lease in expired_leases:
                    self.stdout.write(f"  Processing Lease ID: {lease.id} (End Date: {lease.end_date}) for Property ID: {lease.property.id}")

                    
                    lease.status = LeaseStatus.COMPLETED
                    lease.save()
                    completed_count += 1

                    
                    
                    
                    
                    if lease.property.availability_status == AvailabilityStatus.RENTED:
                         lease.property.availability_status = AvailabilityStatus.AVAILABLE
                         lease.property.save()
                         property_updated_count += 1
                         self.stdout.write(f"    Updated Property ID: {lease.property.id} to AVAILABLE.")
                    else:
                         self.stdout.write(f"    Property ID: {lease.property.id} status was already {lease.property.availability_status}, not changing.")


        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred during transaction: {e}"))
            
            return

        self.stdout.write(self.style.SUCCESS(
            f"Successfully completed {completed_count} leases and updated {property_updated_count} properties."
        ))


# have to use cronjob 
# Schedule the Command (using cron on Linux/macOS)
## Example: Run daily at 3:05 AM
## 5 3 * * * /path/to/your/project/venv/bin/python /path/to/your/project/manage.py update_lease_status >> /path/to/your/project/logs/cron_lease_updates.log 2>&1