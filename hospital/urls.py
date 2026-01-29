from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('signup/', views.signup, name='signup'),
    path('signup-success/', views.signup_success, name='signup_success'),
    path('login/', auth_views.LoginView.as_view(template_name='hospital/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # path('predict/', views.predict, name='predict'),
    # Prediction URLs
    path('predict/', views.predict, name='predict'),  # Initial prediction
    path('predict/<int:patient_id>/', views.predict, name='repredict'),  # ⭐ NEW: Reprediction
    path('prediction-history/<int:patient_id>/', views.view_prediction_history, name='prediction_history'),  # ⭐ NEW
    path('manage-users/', views.manage_users, name='manage_users'),
    path('ward-availability/', views.ward_availability, name='ward_availability'),
    path('assign-bed/', views.assign_bed, name='assign_bed'),
    path('manage-wards/', views.manage_wards, name='manage_wards'),
    path('patients/', views.view_patients, name='view_patients'),
    path('discharge/<int:admission_id>/', views.discharge_patient, name='discharge_patient'),
    path('discharge-history/', views.discharge_history, name='discharge_history'),
    path('assign-bed-with-prediction/', views.assign_bed_with_prediction, name='assign_bed_with_prediction'),  # NEW
    path('process-assignment/', views.process_bed_assignment, name='process_bed_assignment'),  # NEW
    path('reports/bed-occupancy/', views.bed_occupancy_reports, name='bed_occupancy_reports'),
    path('reports/bed-occupancy/export/', views.export_occupancy_report, name='export_occupancy_report'),
    path('discharge-alerts/', views.discharge_alerts, name='discharge_alerts'),  # ← ADD THIS
    path('bed-availability-forecast/', views.bed_availability_forecast, name='bed_availability_forecast'),  # ← ADD THIS

]
