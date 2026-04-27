from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

# HOSPITAL MODEL
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def total_beds(self):
        return Bed.objects.filter(ward__hospital=self, is_operational=True).count()

    def available_beds(self):
        return Bed.objects.filter(ward__hospital=self, is_operational=True, is_occupied=False).count()

    def occupied_beds(self):
        return Bed.objects.filter(ward__hospital=self, is_operational=True, is_occupied=True).count()

    def occupancy_rate(self):
        total = self.total_beds()
        if total == 0:
            return 0
        return round((self.occupied_beds() / total) * 100, 1)

    class Meta:
        ordering = ['name']

# PROFILE MODEL
class Profile(models.Model):
    ROLE_CHOICES = (
        ('pending', 'Pending Approval'),
        ('nurse', 'Nurse'),
        ('hospital_staff', 'Hospital Staff'),
        ('it_support', 'IT Support'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='staff'
    )
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
    
    # Personal Info
    # Personal Info
    full_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        hospital_name = self.hospital.name if self.hospital else 'No Hospital'
        status = 'Approved' if self.is_approved else 'Pending'
        return f"{self.user.username} - {self.role} ({status}) [{hospital_name}]"

# WARD MODEL
class Ward(models.Model):
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

    GENDER_RESTRICTION_CHOICES = (
        ('male', 'Male Only'),
        ('female', 'Female Only'),
        ('mixed', 'Mixed Gender'),
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='wards',
        null=True  
    )
    name = models.CharField(max_length=100)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPE_CHOICES)
    gender_restriction = models.CharField(
        max_length=10,
        choices=GENDER_RESTRICTION_CHOICES,
        default='mixed'
    )
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
        return f"{self.name} ({self.get_ward_type_display()}) — {self.hospital.name if self.hospital else 'No Hospital'}"

    class Meta:
        ordering = ['hospital', 'ward_type', 'name']

# BED MODEL
class Bed(models.Model):
    GENDER_RESTRICTION_CHOICES = (
        ('male', 'Male Only'),
        ('female', 'Female Only'),
        ('mixed', 'Mixed/Any Gender'),
    )

    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=20)
    gender_restriction = models.CharField(
        max_length=10,
        choices=GENDER_RESTRICTION_CHOICES,
        default='mixed'
    )
    is_occupied = models.BooleanField(default=False)
    is_operational = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"{self.bed_number} ({self.ward.name}) - {status}"

    class Meta:
        ordering = ['ward', 'bed_number']
        unique_together = ['ward', 'bed_number']

# PATIENT ADMISSION
class PatientAdmission(models.Model):
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
    
    NHIS_CHOICES = (
    ('yes', 'Yes'),
    ('no', 'No'),
    ('unknown', 'Unknown'),
    )
    nhis_status = models.CharField(max_length=10, choices=NHIS_CHOICES, default='unknown', blank=True)

    # Hospital — direct FK for easy filtering
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='admissions',
        null=True  # temporary
    )

    # Patient Info
    patient_name = models.CharField(max_length=200)
    patient_id = models.CharField(max_length=50, blank=True)  # auto-generated per hospital
    age = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])

    # Additional fields
    contact_number = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    known_allergies = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    # Referral Information
    REFERRAL_TYPE_CHOICES = (
        ('self', 'Self / Walk-in'),
        ('hospital', 'Another Hospital'),
        ('clinic', 'Clinic / Polyclinic'),
        ('community', 'Community Health Centre'),
        ('other', 'Other'),
    )
    referral_type = models.CharField(
        max_length=20,
        choices=REFERRAL_TYPE_CHOICES,
        default='self',
        blank=True
    )
    referral_source = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of referring facility or area"
    )

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
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_patients'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient_name} ({self.patient_id})"

    def days_remaining(self):
        today = date.today()
        if self.predicted_discharge_date:
            return (self.predicted_discharge_date - today).days
        return None

    def save(self, *args, **kwargs):
        """Auto-generate patient_id per hospital if not provided"""
        if not self.patient_id:
            current_year = date.today().year

            # Scoped to hospital if available
            filter_kwargs = {'patient_id__startswith': f'PAT-{current_year}-'}
            if self.hospital:
                filter_kwargs['hospital'] = self.hospital

            last_patient = PatientAdmission.objects.filter(
                **filter_kwargs
            ).order_by('patient_id').last()

            if last_patient:
                last_number = int(last_patient.patient_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.patient_id = f'PAT-{current_year}-{new_number:04d}'

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-admission_date']

# BED OCCUPANCY LOG
class BedOccupancyLog(models.Model):
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='occupancy_logs')
    patient = models.ForeignKey(
        PatientAdmission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Bed Occupancy Log"
        verbose_name_plural = "Bed Occupancy Logs"

    def __str__(self):
        return f"{self.bed.bed_number} - {self.previous_status} → {self.new_status} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"

# DISCHARGE RECORD
class DischargeRecord(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='discharge_records',
        null=True
    )
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
        if self.admission_date and self.actual_discharge_date:
            return (self.actual_discharge_date - self.admission_date).total_seconds() / 86400
        return 0

    def prediction_error(self):
        if self.predicted_los:
            return self.actual_los() - self.predicted_los
        return None

# PREDICTION HISTORY
class PredictionHistory(models.Model):
    patient = models.ForeignKey(
        PatientAdmission,
        on_delete=models.CASCADE,
        related_name='prediction_history'
    )

    predicted_los = models.FloatField(help_text="Predicted Length of Stay in days")
    previous_los = models.FloatField(null=True, blank=True)

    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    admission_type = models.CharField(max_length=50, null=True, blank=True)
    diagnosis = models.CharField(max_length=200, null=True, blank=True)
    severity = models.CharField(max_length=20, null=True, blank=True)
    num_procedures = models.IntegerField(null=True, blank=True)
    num_medications = models.IntegerField(null=True, blank=True)

    predicted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    predicted_at = models.DateTimeField(auto_now_add=True)
    is_initial_prediction = models.BooleanField(default=True)
    reason_for_change = models.TextField(blank=True)

    class Meta:
        ordering = ['-predicted_at']
        verbose_name = "Prediction History"
        verbose_name_plural = "Prediction Histories"

    def __str__(self):
        prediction_type = "Initial" if self.is_initial_prediction else "Reprediction"
        return f"{prediction_type} for {self.patient.patient_name} - {self.predicted_los} days"

    def get_change_amount(self):
        if self.previous_los is not None:
            return self.predicted_los - self.previous_los
        return 0

    def get_change_percentage(self):
        if self.previous_los and self.previous_los != 0:
            change = ((self.predicted_los - self.previous_los) / self.previous_los) * 100
            return round(change, 1)
        return None

    def get_change_direction(self):
        change = self.get_change_amount()
        if change > 0:
            return 'increased'
        elif change < 0:
            return 'decreased'
        return 'no change'
