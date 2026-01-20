# from django.contrib import admin
# from .models import Profile

# admin.site.register(Profile)

from django.contrib import admin
from django.utils import timezone
from .models import Profile, Ward, Bed, PatientAdmission

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_approved', 'approved_by', 'approved_at')
    list_filter = ('role', 'is_approved')
    search_fields = ('user__username', 'user__email')
    list_editable = ('role', 'is_approved')


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'ward_type', 'floor', 'total_beds', 'available_beds_count', 'occupancy_rate')
    list_filter = ('ward_type', 'floor')
    search_fields = ('name',)
    
    def occupancy_rate(self, obj):
        return f"{obj.occupancy_rate():.1f}%"
    occupancy_rate.short_description = 'Occupancy'


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'ward', 'is_occupied', 'is_operational')
    list_filter = ('is_occupied', 'is_operational', 'ward')
    search_fields = ('bed_number',)
    list_editable = ('is_occupied', 'is_operational')


@admin.register(PatientAdmission)
class PatientAdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_id', 'bed', 'admission_date', 'status', 'assigned_by')
    list_filter = ('status', 'admission_date', 'gender')
    search_fields = ('patient_name', 'patient_id')
    date_hierarchy = 'admission_date'