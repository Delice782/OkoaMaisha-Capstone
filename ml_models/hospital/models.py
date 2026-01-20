# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone

# class Profile(models.Model):
#     ROLE_CHOICES = (
#         ('pending', 'Pending Approval'),
#         ('nurse', 'Nurse'),
#         ('hospital_staff', 'Hospital Staff'),
#         ('it_support', 'IT Support'),
#     )
    
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pending')
#     is_approved = models.BooleanField(default=False)
#     approved_by = models.ForeignKey(
#         User, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         related_name='approved_users'
#     )
#     approved_at = models.DateTimeField(null=True, blank=True)
    
#     def __str__(self):
#         status = 'Approved' if self.is_approved else 'Pending'
#         return f"{self.user.username} - {self.role} ({status})"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

# Existing Profile model stays as is
class Profile(models.Model):
    ROLE_CHOICES = (
        ('pending', 'Pending Approval'),
        ('nurse', 'Nurse'),
        ('hospital_staff', 'Hospital Staff'),
        ('it_support', 'IT Support'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pending')
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_users'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        status = 'Approved' if self.is_approved else 'Pending'
        return f"{self.user.username} - {self.role} ({status})"


# NEW MODELS - Add these below Profile
class Ward(models.Model):
    """Departments/Units within the hospital"""
    WARD_TYPE_CHOICES = (
        ('icu', 'Intensive Care Unit'),
        ('general', 'General Ward'),
        ('maternity', 'Maternity'),
        ('pediatric', 'Pediatrics'),
        ('surgery', 'Surgery'),
        ('emergency', 'Emergency'),
        ('cardiology', 'Cardiology'),
        ('orthopedic', 'Orthopedic'),
    )
    
    name = models.CharField(max_length=100)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPE_CHOICES)
    floor = models.IntegerField(null=True, blank=True)
    total_beds = models.IntegerField()
    description = models.TextField(blank=True)
    
    def available_beds_count(self):
        occupied = Bed.objects.filter(ward=self, is_occupied=True, is_operational=True).count()
        operational = Bed.objects.filter(ward=self, is_operational=True).count()
        return operational - occupied
    
    def occupancy_rate(self):
        operational = Bed.objects.filter(ward=self, is_operational=True).count()
        if operational == 0:
            return 0
        occupied = Bed.objects.filter(ward=self, is_occupied=True, is_operational=True).count()
        return (occupied / operational * 100)
    
    def __str__(self):
        return f"{self.name} ({self.get_ward_type_display()})"
    
    class Meta:
        ordering = ['ward_type', 'name']


class Bed(models.Model):
    """Individual beds within wards"""
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)
    is_operational = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"{self.bed_number} ({self.ward.name}) - {status}"
    
    class Meta:
        ordering = ['ward', 'bed_number']
        unique_together = ['ward', 'bed_number']


class PatientAdmission(models.Model):
    """Patient records and bed assignments"""
    STATUS_CHOICES = (
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
    )
    
    # Patient Info
    patient_name = models.CharField(max_length=200)
    patient_id = models.CharField(max_length=50, unique=True, blank=True)  # ← blank=True allows auto-generation
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    
    # Bed Assignment
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, related_name='admissions')
    
    # Dates
    admission_date = models.DateTimeField(auto_now_add=True)
    predicted_los = models.FloatField(null=True, blank=True)
    predicted_discharge_date = models.DateField(null=True, blank=True)
    actual_discharge_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='admitted')
    
    # Tracking
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_patients')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.patient_name} ({self.patient_id})"
    
    class Meta:
        ordering = ['-admission_date']
        
    def save(self, *args, **kwargs):
        """Auto-generate patient_id if not provided"""
        if not self.patient_id:
            # Get current year
            current_year = date.today().year
            
            # Find the latest patient ID for this year
            last_patient = PatientAdmission.objects.filter(
                patient_id__startswith=f'PAT-{current_year}-'
            ).order_by('patient_id').last()
            
            if last_patient:
                # Extract the number and increment
                last_number = int(last_patient.patient_id.split('-')[-1])
                new_number = last_number + 1
            else:
                # First patient of the year
                new_number = 1
            
            # Generate new ID: PAT-2025-0001
            self.patient_id = f'PAT-{current_year}-{new_number:04d}'
        
        super().save(*args, **kwargs)
    