from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # AUTHENTICATION
    path('login/', auth_views.LoginView.as_view(template_name='hospital/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),
    
    # MAIN PAGES
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # PATIENT MANAGEMENT 
    path('patient/details/', views.patient_detail, name='patient_detail'),
    path('patient/discharge/', views.discharge_patient, name='discharge_patient'),
    path('patient/history/', views.view_prediction_history, name='prediction_history'),
    path('patients/', views.view_patients, name='view_patients'),
    path('discharge-history/', views.discharge_history, name='discharge_history'),
    
    # PREDICTION & BED ASSIGNMENT
    path('predict/', views.predict, name='predict'),
    path('patient/repredict/', views.predict, name='repredict'),  # Clean URL for repredict
    path('assign-bed/', views.assign_bed, name='assign_bed'),
    path('assign-bed-with-prediction/', views.assign_bed_with_prediction, name='assign_bed_with_prediction'),
    path('process-bed-assignment/', views.process_bed_assignment, name='process_bed_assignment'),
    
    # WARD MANAGEMENT
    path('wards/', views.ward_availability, name='ward_availability'),
    path('manage-wards/', views.manage_wards, name='manage_wards'),
    
    # REPORTS & ANALYTICS
    path('bed-occupancy-reports/', views.bed_occupancy_reports, name='bed_occupancy_reports'),
    path('discharge-alerts/', views.discharge_alerts, name='discharge_alerts'),
    path('bed-availability-forecast/', views.bed_availability_forecast, name='bed_availability_forecast'),
    path('export-occupancy-report/', views.export_occupancy_report, name='export_occupancy_report'),
    path('referral-analytics/', views.referral_analytics, name='referral_analytics'),
    
    # CROSS-HOSPITAL (Referral Feature)
    path('cross-hospital-availability/', views.cross_hospital_availability, name='cross_hospital_availability'),
    
    # USER MANAGEMENT (IT Support)
    path('manage-users/', views.manage_users, name='manage_users'),
]
