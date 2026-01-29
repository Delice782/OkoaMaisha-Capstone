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
# from .models import BedStatusLog  # Remove this


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
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )
    
    # Patient Info
    # patient_name = models.CharField(max_length=200)
    # patient_id = models.CharField(max_length=50, unique=True, blank=True)  # ← blank=True allows auto-generation
    # age = models.IntegerField(null=True, blank=True)
    # gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    
    patient_name = models.CharField(max_length=200)
    patient_id = models.CharField(max_length=50, unique=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  # NEW
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    
    # NEW FIELDS
    contact_number = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    known_allergies = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    
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
    
# bed occupancy log model for hospital staff
class BedOccupancyLog(models.Model):
    """Track bed status changes for occupancy analytics"""
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='occupancy_logs')
    patient = models.ForeignKey(PatientAdmission, on_delete=models.SET_NULL, null=True, blank=True)
    previous_status = models.CharField(max_length=20)  # 'available', 'occupied'
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)  # 'admission', 'discharge', 'transfer'
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Bed Occupancy Log"
        verbose_name_plural = "Bed Occupancy Logs"
    
    def __str__(self):
        return f"{self.bed.bed_number} - {self.previous_status} → {self.new_status} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"


class DischargeRecord(models.Model):
    """Separate model to store discharge analytics"""
    patient_name = models.CharField(max_length=200)
    patient_id = models.CharField(max_length=50)
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True)
    
    admission_date = models.DateTimeField()
    actual_discharge_date = models.DateTimeField()
    predicted_los = models.FloatField(null=True, blank=True)
    
    discharged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-actual_discharge_date']
    
    def actual_los(self):
        """Calculate actual length of stay in days"""
        if self.admission_date and self.actual_discharge_date:
            return (self.actual_discharge_date - self.admission_date).total_seconds() / 86400
        return 0
    
    def prediction_error(self):
        """Calculate prediction error"""
        if self.predicted_los:
            return self.actual_los() - self.predicted_los
        return None

# class BedStatusLog(models.Model):
#     """Track all bed status changes for auditing and analytics"""
#     bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='status_logs')
#     patient = models.ForeignKey(PatientAdmission, on_delete=models.SET_NULL, null=True, blank=True)
    
#     previous_status = models.CharField(max_length=20)
#     new_status = models.CharField(max_length=20)
    
#     changed_at = models.DateTimeField(auto_now_add=True)
#     changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     reason = models.CharField(max_length=200, blank=True)
#     notes = models.TextField(blank=True)
    
#     class Meta:
#         ordering = ['-changed_at']
#         verbose_name = "Bed Status Log"
#         verbose_name_plural = "Bed Status Logs"
    
#     def __str__(self):
#         return f"{self.bed.bed_number}: {self.previous_status} → {self.new_status} at {self.changed_at.strftime('%Y-%m-%d %H:%M')}"

class PredictionHistory(models.Model):
    """Track all LoS predictions and repredictions for patients"""
    patient = models.ForeignKey(
        PatientAdmission, 
        on_delete=models.CASCADE, 
        related_name='prediction_history'
    )
    
    # Prediction results
    predicted_los = models.FloatField(help_text="Predicted Length of Stay in days")
    previous_los = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Previous prediction (for repredictions)"
    )
    
    # Input features used for this prediction
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    admission_type = models.CharField(max_length=50, null=True, blank=True)
    diagnosis = models.CharField(max_length=200, null=True, blank=True)
    severity = models.CharField(max_length=20, null=True, blank=True)
    num_procedures = models.IntegerField(null=True, blank=True)
    num_medications = models.IntegerField(null=True, blank=True)
    
    # Tracking info
    predicted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Staff member who made the prediction"
    )
    predicted_at = models.DateTimeField(auto_now_add=True)
    is_initial_prediction = models.BooleanField(
        default=True, 
        help_text="True if first prediction, False if reprediction"
    )
    reason_for_change = models.TextField(
        blank=True, 
        help_text="Why was reprediction needed? (e.g., 'Post-surgery', 'Patient condition improved')"
    )
    
    class Meta:
        ordering = ['-predicted_at']
        verbose_name = "Prediction History"
        verbose_name_plural = "Prediction Histories"
    
    def __str__(self):
        prediction_type = "Initial" if self.is_initial_prediction else "Reprediction"
        return f"{prediction_type} for {self.patient.patient_name} - {self.predicted_los} days"
    
    def get_change_amount(self):
        """Calculate how much the prediction changed"""
        if self.previous_los is not None:
            return self.predicted_los - self.previous_los
        return 0
    
    def get_change_percentage(self):
        """Calculate percentage change from previous prediction"""
        if self.previous_los and self.previous_los != 0:
            change = ((self.predicted_los - self.previous_los) / self.previous_los) * 100
            return round(change, 1)
        return None
    
    def get_change_direction(self):
        """Returns 'increased', 'decreased', or 'no change'"""
        change = self.get_change_amount()
        if change > 0:
            return 'increased'
        elif change < 0:
            return 'decreased'
        return 'no change'