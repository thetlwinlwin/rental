from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Lease(models.Model):
    class LeaseStatus(models.TextChoices):
        PENDING = 'PE', 'Pending Approval'
        ACTIVE = 'AC', 'Active'
        COMPLETED = 'CO', 'Completed'
        CANCELLED = 'CA', 'Cancelled'
        REJECTED = 'RE', 'Rejected'

    property = models.ForeignKey(
        'properties.Property',
        related_name='leases',
        on_delete=models.PROTECT, 
        help_text="The property being leased."
    )
    tenant = models.ForeignKey(
        User, 
        related_name='leases_held',
        on_delete=models.PROTECT, 
        help_text="The user (Tenant) leasing the property."
    )
    start_date = models.DateField(help_text="The official start date of the lease term.")
    end_date = models.DateField(help_text="The official end date of the lease term.")
    status = models.CharField(
        max_length=2,
        choices=LeaseStatus.choices,
        default=LeaseStatus.PENDING,
        help_text="The current status of the lease agreement."
    )
    monthly_rent_at_signing = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monthly rent amount agreed upon in the lease."
    )
    deposit_paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Amount of the security deposit actually paid."
    )
    deposit_paid_date = models.DateField(blank=True, null=True, help_text="Date the deposit was paid.")
    lease_document = models.FileField(
        upload_to='lease_documents/',
        blank=True,
        null=True,
        help_text="Optional scanned copy of the signed lease agreement."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the lease record was created/application submitted.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lease"
        verbose_name_plural = "Leases"
        ordering = ['-start_date', '-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='lease_end_date_gte_start_date')
        ]

    def __str__(self):
        return f"Lease for '{self.property.title}' by {self.tenant.username} ({self.start_date} to {self.end_date})"

class Review(models.Model):
    """
    Represents a review left by a tenant about a specific lease/property/landlord.
    """
    lease = models.OneToOneField(
        Lease,
        related_name='review',
        on_delete=models.CASCADE, 
        help_text="The specific lease being reviewed."
        
    )
    reviewer = models.ForeignKey(
        User, 
        related_name='reviews_given',
        on_delete=models.SET_NULL, 
        null=True,
        help_text="The user (Tenant) who wrote the review."
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating from 1 (worst) to 5 (best)."
    )
    comment = models.TextField(blank=True, null=True, help_text="Detailed review comment.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']
        

    def __str__(self):
        return f"Review for Lease ID {self.lease.id} by {self.reviewer.username} - {self.rating} Stars"

    
    @property
    def property(self):
        return self.lease.property