# import os
# import joblib
# import pandas as pd
# import numpy as np
# from django.shortcuts import render, redirect
# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
# from django.contrib import messages
# from django.utils import timezone
# from django.db import models  # Add this line with other imports
# from .models import Profile, Ward, Bed, PatientAdmission
# from datetime import date, timedelta

# # --- 1. Load ML artifacts ---
# MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models')

# # These load when the server starts
# model = joblib.load(os.path.join(MODEL_PATH, 'best_model.pkl'))
# scaler = joblib.load(os.path.join(MODEL_PATH, 'scaler.pkl'))
# feature_names = joblib.load(os.path.join(MODEL_PATH, 'feature_names.pkl'))

# # Comorbidity field names
# COMORBIDITY_FIELDS = [
#     'dialysisrenalendstage', 'asthma', 'irondef', 'pneum',
#     'substancedependence', 'psychologicaldisordermajor',
#     'depress', 'psychother', 'fibrosisandother', 'malnutrition', 'hemo'
# ]

# # --- 2. Home View ---
# @login_required
# def home(request):
#     # Check if user is approved
#     if not request.user.profile.is_approved:
#         return render(request, 'hospital/pending.html')
    
#     return render(request, 'hospital/home.html')

# # --- 3. Signup View ---
# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             # Create profile with pending status
#             Profile.objects.create(
#                 user=user,
#                 role='pending',
#                 is_approved=False
#             )
#             return redirect('signup_success')
#     else:
#         form = UserCreationForm()
#     return render(request, 'hospital/signup.html', {'form': form})

# # --- 4. Signup Success View ---
# def signup_success(request):
#     return render(request, 'hospital/signup_success.html')

# # --- 5. Enhanced Prediction View ---
# @login_required
# def predict(request):
#     # Check approval status first
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     # Then check role
#     if request.user.profile.role != 'nurse':
#         return redirect('home')

#     prediction_result = None
#     comorbidity_count = 0
#     rcount = 0
#     risk_score = 0
    
#     if request.method == 'POST':
#         try:
#             # 1. Capture Raw Inputs from HTML
#             raw_input = {
#                 'gender': 1 if request.POST.get('gender') == 'Male' else 0,
#                 'rcount': int(request.POST.get('rcount', 0)),
#                 'bmi': float(request.POST.get('bmi', 25.0)),
#                 'pulse': float(request.POST.get('pulse', 75)),
#                 'respiration': float(request.POST.get('respiration', 16.0)),
#                 'hematocrit': float(request.POST.get('hematocrit', 40.0)),
#                 'neutrophils': float(request.POST.get('neutrophils', 4.0)),
#                 'glucose': float(request.POST.get('glucose', 100)),
#                 'sodium': float(request.POST.get('sodium', 140)),
#                 'creatinine': float(request.POST.get('creatinine', 1.0)),
#                 'bloodureanitro': float(request.POST.get('bloodureanitro', 12.0)),
#                 'facility': request.POST.get('facility', 'A'),
#                 'admission_month': int(request.POST.get('admission_month', 1)),
#                 'admission_dayofweek': int(request.POST.get('admission_dayofweek', 0)),
#                 'secondarydiagnosisnonicd9': int(request.POST.get('secondarydiagnosisnonicd9', 1))
#             }
            
#             # Capture comorbidities
#             comorbidities = {}
#             for field in COMORBIDITY_FIELDS:
#                 comorbidities[field] = 1 if request.POST.get(field) else 0
            
#             # Count comorbidities
#             comorbidity_count = sum(comorbidities.values())
#             rcount = raw_input['rcount']

#             # 2. Create DataFrame with all 42 columns
#             df = pd.DataFrame(0, index=[0], columns=feature_names)

#             # 3. Fill basic columns
#             for col in raw_input:
#                 if col in df.columns:
#                     df[col] = raw_input[col]
            
#             # 4. Fill comorbidity columns
#             for field, value in comorbidities.items():
#                 if field in df.columns:
#                     df[field] = value

#             # 5. Feature Engineering
#             df['total_comorbidities'] = comorbidity_count
#             df['high_glucose'] = int(raw_input['glucose'] > 140)
#             df['low_sodium'] = int(raw_input['sodium'] < 135)
#             df['high_creatinine'] = int(raw_input['creatinine'] > 1.3)
#             df['low_bmi'] = int(raw_input['bmi'] < 18.5)
#             df['high_bmi'] = int(raw_input['bmi'] > 30)
#             df['abnormal_vitals'] = (
#                 int(raw_input['pulse'] < 60 or raw_input['pulse'] > 100) +
#                 int(raw_input['respiration'] < 12 or raw_input['respiration'] > 20)
#             )
            
#             # Admission quarter
#             df['admission_quarter'] = (raw_input['admission_month'] - 1) // 3 + 1
            
#             # Facility one-hot encoding
#             facility_col = f"facility_{raw_input['facility']}"
#             if facility_col in df.columns:
#                 df[facility_col] = 1

#             # 6. Scale and Predict
#             input_scaled = scaler.transform(df)
#             prediction = model.predict(input_scaled)[0]
#             prediction_result = round(prediction, 1)
            
#             # 7. Calculate risk score
#             risk_score = min((comorbidity_count * 10) + (rcount * 15), 100)

#         except Exception as e:
#             prediction_result = None
#             print(f"Prediction Error: {e}")  # For debugging

#     context = {
#         'prediction': prediction_result,
#         'comorbidity_count': comorbidity_count,
#         'rcount': rcount,
#         'risk_score': risk_score,
#     }
    
#     return render(request, 'hospital/predict.html', context)

# # Add to your existing views.py (after predict function)

# @login_required
# def ward_availability(request):
#     # Check approval and role
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     if request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     # Get all wards with stats
#     wards = Ward.objects.all()
    
#     ward_stats = []
#     for ward in wards:
#         operational_beds = Bed.objects.filter(ward=ward, is_operational=True).count()
#         occupied = Bed.objects.filter(ward=ward, is_occupied=True, is_operational=True).count()
#         available = operational_beds - occupied
#         occupancy_rate = (occupied / operational_beds * 100) if operational_beds > 0 else 0
        
#         # Determine status color
#         if available == 0:
#             status = 'full'
#             status_color = '#ef4444'  # red
#         elif occupancy_rate > 80:
#             status = 'almost_full'
#             status_color = '#f59e0b'  # orange
#         else:
#             status = 'available'
#             status_color = '#10b981'  # green
        
#         ward_stats.append({
#             'id': ward.id,
#             'name': ward.name,
#             'type': ward.get_ward_type_display(),
#             'floor': ward.floor,
#             'total': operational_beds,
#             'occupied': occupied,
#             'available': available,
#             'occupancy_rate': round(occupancy_rate, 1),
#             'status': status,
#             'status_color': status_color,
#         })
    
#     context = {'ward_stats': ward_stats}
#     return render(request, 'hospital/ward_availability.html', context)

# # Add after ward_availability function

# @login_required
# def assign_bed(request):
#     # Check approval and role
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     if request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     if request.method == 'POST':
#         try:
#             # Get form data
#             patient_name = request.POST.get('patient_name')
#             patient_id = request.POST.get('patient_id')
#             age = request.POST.get('age')
#             gender = request.POST.get('gender')
#             bed_id = request.POST.get('bed_id')
#             predicted_los = request.POST.get('predicted_los')
#             notes = request.POST.get('notes', '')
            
#             # Get the bed
#             bed = Bed.objects.get(id=bed_id)
            
#             # Check if bed is available
#             if bed.is_occupied:
#                 messages.error(request, f"Bed {bed.bed_number} is already occupied!")
#                 return redirect('assign_bed')
            
#             # Calculate predicted discharge date
#             predicted_discharge = None
#             if predicted_los:
#                 from datetime import timedelta, date
#                 predicted_discharge = date.today() + timedelta(days=float(predicted_los))
            
#             # Create patient admission
#             admission = PatientAdmission.objects.create(
#                 patient_name=patient_name,
#                 patient_id=patient_id,
#                 age=int(age) if age else None,
#                 gender=gender,
#                 bed=bed,
#                 predicted_los=float(predicted_los) if predicted_los else None,
#                 predicted_discharge_date=predicted_discharge,
#                 assigned_by=request.user,
#                 notes=notes,
#                 status='admitted'
#             )
            
#             # Mark bed as occupied
#             bed.is_occupied = True
#             bed.save()
            
#             messages.success(request, f"Patient {patient_name} successfully assigned to Bed {bed.bed_number}")
#             return redirect('assign_bed')
            
#         except Bed.DoesNotExist:
#             messages.error(request, "Selected bed not found")
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
        
#         return redirect('assign_bed')
    
#     # GET request - show form
#     # Get all wards with available beds
#     wards = Ward.objects.all()
    
#     # Get available beds grouped by ward
#     ward_beds = []
#     for ward in wards:
#         available_beds = Bed.objects.filter(
#             ward=ward, 
#             is_occupied=False, 
#             is_operational=True
#         )
        
#         if available_beds.exists():
#             ward_beds.append({
#                 'ward': ward,
#                 'beds': available_beds
#             })
    
#     # Get recent admissions
#     recent_admissions = PatientAdmission.objects.filter(
#         status='admitted'
#     ).select_related('bed', 'bed__ward', 'assigned_by').order_by('-admission_date')[:10]
    
#     context = {
#         'ward_beds': ward_beds,
#         'recent_admissions': recent_admissions,
#     }
    
#     return render(request, 'hospital/assign_bed.html', context)

# from datetime import date, timedelta

# @login_required
# def assign_bed_with_prediction(request):
#     """Assign patient to bed with pre-filled prediction data"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     if request.method == 'POST':
#         # Get prediction data from previous form
#         predicted_los = request.POST.get('predicted_los')
#         comorbidity_count = request.POST.get('comorbidity_count')
#         risk_score = request.POST.get('risk_score')
        
#         # Check for available beds
#         wards = Ward.objects.all()
#         ward_beds = []
        
#         for ward in wards:
#             available_beds = Bed.objects.filter(
#                 ward=ward, 
#                 is_occupied=False, 
#                 is_operational=True
#             )
            
#             if available_beds.exists():
#                 ward_beds.append({
#                     'ward': ward,
#                     'beds': available_beds
#                 })
        
#         # If no beds available, show special message
#         if not ward_beds:
#             # Get stats for no-beds message
#             total_beds = Bed.objects.filter(is_operational=True).count()
#             occupied_beds = Bed.objects.filter(is_occupied=True, is_operational=True).count()
            
#             # Find patients near discharge (within 2 days)
#             near_discharge = []
#             for admission in PatientAdmission.objects.filter(status='admitted').select_related('bed', 'bed__ward'):
#                 if admission.predicted_discharge_date:
#                     days_until = (admission.predicted_discharge_date - date.today()).days
#                     if days_until <= 2:
#                         near_discharge.append({
#                             'admission': admission,
#                             'days_until': days_until
#                         })
            
#             context = {
#                 'no_beds_available': True,
#                 'total_beds': total_beds,
#                 'occupied_beds': occupied_beds,
#                 'near_discharge': near_discharge,
#                 'predicted_los': predicted_los,
#             }
#             return render(request, 'hospital/assign_bed_with_prediction.html', context)
        
#         # Beds available - show normal assignment form with pre-filled data
#         recent_admissions = PatientAdmission.objects.filter(
#             status='admitted'
#         ).select_related('bed', 'bed__ward', 'assigned_by').order_by('-admission_date')[:10]
        
#         context = {
#             'ward_beds': ward_beds,
#             'recent_admissions': recent_admissions,
#             'predicted_los': predicted_los,
#             'comorbidity_count': comorbidity_count,
#             'risk_score': risk_score,
#             'from_prediction': True,
#         }
        
#         return render(request, 'hospital/assign_bed_with_prediction.html', context)
    
#     # GET request - redirect to normal predict page
#     return redirect('predict')

# # @login_required
# # def process_bed_assignment(request):
# #     """Process the actual bed assignment"""
# #     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
# #         return redirect('home')
    
# #     if request.method == 'POST':
# #         try:
# #             # Get form data - NO patient_id needed!
# #             patient_name = request.POST.get('patient_name')
# #             age = request.POST.get('age')
# #             gender = request.POST.get('gender')
# #             bed_id = request.POST.get('bed_id')
# #             predicted_los = request.POST.get('predicted_los')
# #             notes = request.POST.get('notes', '')
            
# #             # Get the bed
# #             bed = Bed.objects.get(id=bed_id)
            
# #             # Check if bed is available
# #             if bed.is_occupied:
# #                 messages.error(request, f"Bed {bed.bed_number} is already occupied!")
# #                 return redirect('assign_bed')
            
# #             # Calculate predicted discharge date
# #             predicted_discharge = None
# #             if predicted_los:
# #                 from datetime import date, timedelta
# #                 predicted_discharge = date.today() + timedelta(days=float(predicted_los))
            
# #             # Create patient admission - patient_id auto-generated!
# #             admission = PatientAdmission.objects.create(
# #                 patient_name=patient_name,
# #                 # patient_id will be auto-generated by the model
# #                 age=int(age) if age else None,
# #                 gender=gender,
# #                 bed=bed,
# #                 predicted_los=float(predicted_los) if predicted_los else None,
# #                 predicted_discharge_date=predicted_discharge,
# #                 assigned_by=request.user,
# #                 notes=notes,
# #                 status='admitted'
# #             )
            
# #             # Mark bed as occupied
# #             bed.is_occupied = True
# #             bed.save()
            
# #             messages.success(request, f"✅ Patient {patient_name} (ID: {admission.patient_id}) successfully assigned to Bed {bed.bed_number}. Predicted discharge: {predicted_discharge.strftime('%b %d, %Y') if predicted_discharge else 'N/A'}")
# #             return redirect('view_patients')
            
# #         except Bed.DoesNotExist:
# #             messages.error(request, "Selected bed not found")
# #         except Exception as e:
# #             messages.error(request, f"Error: {str(e)}")
        
# #         return redirect('assign_bed')
    
# #     return redirect('assign_bed')

# @login_required
# def process_bed_assignment(request):
#     """Process the actual bed assignment"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     if request.method == 'POST':
#         try:
#             # Get form data
#             patient_name = request.POST.get('patient_name')
#             age = request.POST.get('age')
#             gender = request.POST.get('gender')
#             bed_id = request.POST.get('bed_id')
#             predicted_los = request.POST.get('predicted_los')
#             notes = request.POST.get('notes', '')
            
#             # Get the bed
#             bed = Bed.objects.get(id=bed_id)
            
#             # Check if bed is available
#             if bed.is_occupied:
#                 messages.error(request, f"Bed {bed.bed_number} is already occupied!")
#                 return redirect('assign_bed')
            
#             # Calculate predicted discharge date
#             predicted_discharge = None
#             if predicted_los:
#                 from datetime import date, timedelta
#                 predicted_discharge = date.today() + timedelta(days=float(predicted_los))
            
#             # Create patient admission
#             admission = PatientAdmission.objects.create(
#                 patient_name=patient_name,
#                 age=int(age) if age else None,
#                 gender=gender,
#                 bed=bed,
#                 predicted_los=float(predicted_los) if predicted_los else None,
#                 predicted_discharge_date=predicted_discharge,
#                 assigned_by=request.user,
#                 notes=notes,
#                 status='admitted'
#             )
            
#             # Mark bed as occupied
#             previous_status = 'available' if not bed.is_occupied else 'occupied'
#             bed.is_occupied = True
#             bed.save()
            
#             # # ⭐ NEW: Log the bed status change
#             # BedStatusLog.objects.create(
#             #     bed=bed,
#             #     patient=admission,
#             #     previous_status=previous_status,
#             #     new_status='occupied',
#             #     changed_by=request.user,
#             #     reason='patient_admission',
#             #     notes=f"Patient {patient_name} (ID: {admission.patient_id}) admitted"
#             # )
            
#             messages.success(request, f"✅ Patient {patient_name} (ID: {admission.patient_id}) successfully assigned to Bed {bed.bed_number}. Predicted discharge: {predicted_discharge.strftime('%b %d, %Y') if predicted_discharge else 'N/A'}")
#             return redirect('view_patients')
            
#         except Bed.DoesNotExist:
#             messages.error(request, "Selected bed not found")
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
        
#         return redirect('assign_bed')
    
#     return redirect('assign_bed')

# # @login_required
# # def discharge_patient(request, admission_id):
# #     """Discharge a patient and free up their bed"""
# #     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
# #         return redirect('home')
    
# #     try:
# #         admission = PatientAdmission.objects.get(id=admission_id, status='admitted')
        
# #         if request.method == 'POST':
# #             # Mark patient as discharged
# #             admission.status = 'discharged'
# #             admission.actual_discharge_date = timezone.now()
# #             admission.save()
            
# #             # Free up the bed
# #             if admission.bed:
# #                 admission.bed.is_occupied = False
# #                 admission.bed.save()
            
# #             messages.success(request, f"Patient {admission.patient_name} discharged successfully. Bed {admission.bed.bed_number} is now available.")
# #             return redirect('view_patients')
        
# #         # GET - show confirmation page
# #         context = {
# #             'admission': admission,
# #         }
# #         return render(request, 'hospital/discharge_confirm.html', context)
        
# #     except PatientAdmission.DoesNotExist:
# #         messages.error(request, "Patient not found or already discharged")
# #         return redirect('view_patients')

# @login_required
# def discharge_patient(request, admission_id):
#     """Discharge a patient and free up their bed"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     try:
#         admission = PatientAdmission.objects.get(id=admission_id, status='admitted')
        
#         if request.method == 'POST':
#             # Mark patient as discharged
#             admission.status = 'discharged'
#             admission.actual_discharge_date = timezone.now()
#             admission.save()
            
#             # Free up the bed
#             if admission.bed:
#                 bed = admission.bed
#                 bed.is_occupied = False
#                 bed.save()
                
#                 # ⭐ NEW: Log the bed status change
#                 # BedStatusLog.objects.create(
#                 #     bed=bed,
#                 #     patient=admission,
#                 #     previous_status='occupied',
#                 #     new_status='available',
#                 #     changed_by=request.user,
#                 #     reason='patient_discharge',
#                 #     notes=f"Patient {admission.patient_name} (ID: {admission.patient_id}) discharged"
#                 # )
            
#             messages.success(request, f"Patient {admission.patient_name} discharged successfully. Bed {admission.bed.bed_number} is now available.")
#             return redirect('view_patients')
        
#         # GET - show confirmation page
#         context = {
#             'admission': admission,
#         }
#         return render(request, 'hospital/discharge_confirm.html', context)
        
#     except PatientAdmission.DoesNotExist:
#         messages.error(request, "Patient not found or already discharged")
#         return redirect('view_patients')

# @login_required
# def view_patients(request):
#     """View all admitted patients"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     # Get filter parameters
#     ward_filter = request.GET.get('ward', '')
#     search_query = request.GET.get('search', '')
    
#     # Base query - only admitted patients
#     patients = PatientAdmission.objects.filter(status='admitted').select_related('bed', 'bed__ward', 'assigned_by')
    
#     # Apply filters
#     if ward_filter:
#         patients = patients.filter(bed__ward__id=ward_filter)
    
#     if search_query:
#         patients = patients.filter(
#             models.Q(patient_name__icontains=search_query) |
#             models.Q(patient_id__icontains=search_query)
#         )
    
#     # Order by most recent first
#     patients = patients.order_by('-admission_date')
    
#     # Get all wards for filter dropdown
#     wards = Ward.objects.all()
    
#     # Calculate stats
#     total_patients = patients.count()
    
#     context = {
#         'patients': patients,
#         'wards': wards,
#         'total_patients': total_patients,
#         'ward_filter': ward_filter,
#         'search_query': search_query,
#     }
    
#     return render(request, 'hospital/view_patients.html', context)

# @login_required
# def discharge_history(request):
#     """View all discharged patients with stats"""
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     # Only nurses and hospital_staff can view
#     if request.user.profile.role not in ['nurse', 'hospital_staff']:
#         return redirect('home')
    
#     # Get filter parameters
#     ward_filter = request.GET.get('ward', '')
#     search_query = request.GET.get('search', '')
#     date_from = request.GET.get('date_from', '')
#     date_to = request.GET.get('date_to', '')
    
#     # Base query - only discharged patients
#     discharges = PatientAdmission.objects.filter(status='discharged').select_related('bed', 'bed__ward', 'assigned_by')
    
#     # Apply filters
#     if ward_filter:
#         discharges = discharges.filter(bed__ward__id=ward_filter)
    
#     if search_query:
#         discharges = discharges.filter(
#             models.Q(patient_name__icontains=search_query) |
#             models.Q(patient_id__icontains=search_query)
#         )
    
#     if date_from:
#         discharges = discharges.filter(actual_discharge_date__gte=date_from)
    
#     if date_to:
#         from datetime import datetime, timedelta
#         # Add one day to include the entire end date
#         date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
#         discharges = discharges.filter(actual_discharge_date__lt=date_to_obj)
    
#     # Order by most recent discharge first
#     discharges = discharges.order_by('-actual_discharge_date')
    
#     # Calculate actual length of stay for each discharge
#     discharge_data = []
#     total_predicted_error = 0
#     predictions_count = 0
    
#     for discharge in discharges:
#         if discharge.admission_date and discharge.actual_discharge_date:
#             # Calculate actual LoS in days
#             actual_los = (discharge.actual_discharge_date - discharge.admission_date).total_seconds() / 86400
#             actual_los = round(actual_los, 1)
            
#             # Calculate prediction error if predicted LoS exists
#             prediction_error = None
#             accuracy_class = ''
            
#             if discharge.predicted_los:
#                 prediction_error = actual_los - discharge.predicted_los
#                 total_predicted_error += abs(prediction_error)
#                 predictions_count += 1
                
#                 # Classify accuracy
#                 if abs(prediction_error) <= 0.5:
#                     accuracy_class = 'excellent'  # Green
#                 elif abs(prediction_error) <= 1.5:
#                     accuracy_class = 'good'  # Yellow
#                 else:
#                     accuracy_class = 'poor'  # Red
            
#             discharge_data.append({
#                 'discharge': discharge,
#                 'actual_los': actual_los,
#                 'prediction_error': prediction_error,
#                 'accuracy_class': accuracy_class
#             })
    
#     # Calculate overall stats
#     total_discharges = len(discharge_data)
#     avg_error = round(total_predicted_error / predictions_count, 2) if predictions_count > 0 else 0
    
#     # Get all wards for filter dropdown
#     wards = Ward.objects.all()
    
#     context = {
#         'discharge_data': discharge_data,
#         'wards': wards,
#         'total_discharges': total_discharges,
#         'avg_error': avg_error,
#         'predictions_count': predictions_count,
#         'ward_filter': ward_filter,
#         'search_query': search_query,
#         'date_from': date_from,
#         'date_to': date_to,
#     }
    
#     return render(request, 'hospital/discharge_history.html', context)

# # --- 6. User Management View (IT Support) ---
# @login_required
# def manage_users(request):
#     # Only IT Support can access
#     if not request.user.profile.is_approved or request.user.profile.role != 'it_support':
#         return redirect('home')
    
#     pending_users = Profile.objects.filter(is_approved=False).select_related('user')
#     approved_users = Profile.objects.filter(is_approved=True).select_related('user')
    
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         user_id = request.POST.get('user_id')
        
#         try:
#             if action == 'create':
#                 # CREATE NEW USER
#                 username = request.POST.get('username')
#                 email = request.POST.get('email')
#                 password = request.POST.get('password')
#                 role = request.POST.get('role')
                
#                 # Check if username exists
#                 if User.objects.filter(username=username).exists():
#                     messages.error(request, f"Username '{username}' already exists")
#                 else:
#                     new_user = User.objects.create_user(
#                         username=username,
#                         email=email,
#                         password=password
#                     )
#                     Profile.objects.create(
#                         user=new_user,
#                         role=role,
#                         is_approved=True,
#                         approved_by=request.user,
#                         approved_at=timezone.now()
#                     )
#                     messages.success(request, f"User '{username}' created successfully")
            
#             elif action == 'approve':
#                 # APPROVE PENDING USER
#                 profile = Profile.objects.get(user_id=user_id)
#                 new_role = request.POST.get('role')
#                 profile.role = new_role
#                 profile.is_approved = True
#                 profile.approved_by = request.user
#                 profile.approved_at = timezone.now()
#                 profile.save()
#                 messages.success(request, f"User '{profile.user.username}' approved as {profile.get_role_display()}")
            
#             elif action == 'edit':
#                 # EDIT USER (username, email, role)
#                 profile = Profile.objects.get(user_id=user_id)
#                 new_username = request.POST.get('username')
#                 new_email = request.POST.get('email')
#                 new_role = request.POST.get('role')
                
#                 # Update User model
#                 profile.user.username = new_username
#                 profile.user.email = new_email
#                 profile.user.save()
                
#                 # Update Profile model
#                 profile.role = new_role
#                 profile.save()
                
#                 messages.success(request, f"User '{new_username}' updated successfully")
            
#             elif action == 'change_password':
#                 # CHANGE USER PASSWORD
#                 profile = Profile.objects.get(user_id=user_id)
#                 new_password = request.POST.get('new_password')
#                 profile.user.set_password(new_password)
#                 profile.user.save()
#                 messages.success(request, f"Password changed for '{profile.user.username}'")
            
#             elif action == 'delete':
#                 # DELETE USER
#                 profile = Profile.objects.get(user_id=user_id)
#                 username = profile.user.username
#                 profile.user.delete()  # Cascade deletes profile too
#                 messages.success(request, f"User '{username}' deleted successfully")
            
#             elif action == 'reject':
#                 # REJECT PENDING USER (same as delete)
#                 profile = Profile.objects.get(user_id=user_id)
#                 username = profile.user.username
#                 profile.user.delete()
#                 messages.success(request, f"User '{username}' rejected and deleted")
                
#         except Profile.DoesNotExist:
#             messages.error(request, "User not found")
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
        
#         return redirect('manage_users')
    
#     context = {
#         'pending_users': pending_users,
#         'approved_users': approved_users,
#     }
#     return render(request, 'hospital/manage_users.html', context)

# @login_required
# def manage_wards(request):
#     """IT Support manages wards and beds"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'it_support':
#         return redirect('home')
    
#     if request.method == 'POST':
#         action = request.POST.get('action')
        
#         try:
#             if action == 'create_ward':
#                 ward = Ward.objects.create(
#                     name=request.POST.get('name'),
#                     ward_type=request.POST.get('ward_type'),
#                     floor=request.POST.get('floor') if request.POST.get('floor') else None,
#                     total_beds=int(request.POST.get('total_beds')),
#                     description=request.POST.get('description', '')
#                 )
#                 messages.success(request, f"Ward '{ward.name}' created successfully")
            
#             elif action == 'generate_beds':
#                 ward_id = request.POST.get('ward_id')
#                 ward = Ward.objects.get(id=ward_id)
#                 bed_prefix = request.POST.get('bed_prefix')
#                 start_number = int(request.POST.get('start_number'))
                
#                 # Generate beds
#                 for i in range(ward.total_beds):
#                     bed_number = f"{bed_prefix}-{start_number + i}"
#                     Bed.objects.get_or_create(
#                         ward=ward,
#                         bed_number=bed_number,
#                         defaults={'is_operational': True, 'is_occupied': False}
#                     )
                
#                 messages.success(request, f"{ward.total_beds} beds generated for {ward.name}")
            
#             elif action == 'delete_ward':
#                 ward_id = request.POST.get('ward_id')
#                 ward = Ward.objects.get(id=ward_id)
#                 ward_name = ward.name
#                 ward.delete()
#                 messages.success(request, f"Ward '{ward_name}' deleted")
            
#             elif action == 'delete_bed':
#                 bed_id = request.POST.get('bed_id')
#                 bed = Bed.objects.get(id=bed_id)
#                 bed_number = bed.bed_number
#                 bed.delete()
#                 messages.success(request, f"Bed '{bed_number}' deleted")
                
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
        
#         return redirect('manage_wards')
    
#     # GET - display wards and beds
#     wards = Ward.objects.prefetch_related('beds').all()
    
#     context = {
#         'wards': wards,
#         'ward_types': Ward.WARD_TYPE_CHOICES,
#     }
    
#     return render(request, 'hospital/manage_wards.html', context)

# # bed occupancy report for hospital staff
# @login_required
# def bed_occupancy_reports(request):
#     """Main bed occupancy dashboard with multiple views"""
    
#     # Check approval and role
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     if request.user.profile.role != 'hospital_staff':
#         return redirect('home')
    
#     # Get filter parameters
#     ward_filter = request.GET.get('ward', '')
#     date_from = request.GET.get('date_from', '')
#     date_to = request.GET.get('date_to', '')
    
#     # Parse dates
#     from datetime import datetime, timedelta
#     if date_from:
#         start_date = datetime.strptime(date_from, '%Y-%m-%d')
#     else:
#         start_date = timezone.now() - timedelta(days=30)
    
#     if date_to:
#         date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
#         end_date = date_to_obj
#     else:
#         end_date = timezone.now()
    
#     # === CURRENT OCCUPANCY SNAPSHOT ===
#     current_stats = []
#     total_beds = 0
#     total_occupied = 0
#     total_available = 0
#     total_maintenance = 0
    
#     for ward in Ward.objects.all():
#         ward_beds = Bed.objects.filter(ward=ward, is_operational=True)
#         occupied = ward_beds.filter(is_occupied=True).count()
#         available = ward_beds.filter(is_occupied=False).count()
#         total = ward_beds.count()
        
#         occupancy_rate = (occupied / total * 100) if total > 0 else 0
        
#         current_stats.append({
#             'ward': ward,
#             'total_beds': total,
#             'occupied': occupied,
#             'available': available,
#             'occupancy_rate': round(occupancy_rate, 1)
#         })
        
#         total_beds += total
#         total_occupied += occupied
#         total_available += available
    
#     overall_occupancy_rate = (total_occupied / total_beds * 100) if total_beds > 0 else 0
    
#     # === HISTORICAL DATA ===
#     # Get all discharged patients in date range
#     discharges = PatientAdmission.objects.filter(
#         status='discharged',
#         actual_discharge_date__range=[start_date, end_date]
#     )
    
#     if ward_filter:
#         discharges = discharges.filter(bed__ward_id=ward_filter)
    
#     # Calculate average length of stay
#     total_los = 0
#     los_count = 0
    
#     for discharge in discharges:
#         if discharge.admission_date and discharge.actual_discharge_date:
#             los = (discharge.actual_discharge_date - discharge.admission_date).total_seconds() / 86400
#             total_los += los
#             los_count += 1
    
#     avg_los_days = round(total_los / los_count, 1) if los_count > 0 else 0
    
#     # === BED TURNOVER RATE ===
#     total_discharges = discharges.count()
#     days_in_period = (end_date - start_date).days or 1
#     turnover_rate = (total_discharges / total_beds / days_in_period * 100) if total_beds > 0 else 0
    
#     # === CURRENT PATIENTS WITH PREDICTED DISCHARGE ===
#     current_patients = PatientAdmission.objects.filter(
#         status='admitted'
#     ).select_related('bed', 'bed__ward')
    
#     if ward_filter:
#         current_patients = current_patients.filter(bed__ward_id=ward_filter)
    
#     patients_with_predictions = []
#     for patient in current_patients:
#         if patient.predicted_discharge_date:
#             days_remaining = (patient.predicted_discharge_date - date.today()).days
            
#             patients_with_predictions.append({
#                 'patient': patient,
#                 'expected_discharge': patient.predicted_discharge_date,
#                 'days_remaining': days_remaining,
#                 'ward': patient.bed.ward.name if patient.bed else 'N/A',
#                 'bed': patient.bed.bed_number if patient.bed else 'N/A'
#             })
    
#     # Sort by expected discharge date
#     patients_with_predictions.sort(key=lambda x: x['expected_discharge'])
    
#     # === WARD COMPARISON ===
#     ward_comparison = []
#     for ward in Ward.objects.all():
#         ward_discharges = PatientAdmission.objects.filter(
#             bed__ward=ward,
#             status='discharged',
#             actual_discharge_date__range=[start_date, end_date]
#         )
        
#         ward_total_los = 0
#         ward_los_count = 0
        
#         for discharge in ward_discharges:
#             if discharge.admission_date and discharge.actual_discharge_date:
#                 los = (discharge.actual_discharge_date - discharge.admission_date).total_seconds() / 86400
#                 ward_total_los += los
#                 ward_los_count += 1
        
#         ward_avg_los = round(ward_total_los / ward_los_count, 1) if ward_los_count > 0 else 0
        
#         ward_comparison.append({
#             'ward': ward,
#             'total_discharges': ward_discharges.count(),
#             'avg_los': ward_avg_los
#         })
    
#     context = {
#         'current_stats': current_stats,
#         'overall_occupancy_rate': round(overall_occupancy_rate, 1),
#         'total_beds': total_beds,
#         'total_occupied': total_occupied,
#         'total_available': total_available,
#         'avg_los_days': avg_los_days,
#         'total_discharges': total_discharges,
#         'turnover_rate': round(turnover_rate, 2),
#         'patients_with_predictions': patients_with_predictions[:10],
#         'ward_comparison': ward_comparison,
#         'wards': Ward.objects.all(),
#         'ward_filter': ward_filter,
#         'date_from': date_from or start_date.strftime('%Y-%m-%d'),
#         'date_to': date_to or end_date.strftime('%Y-%m-%d'),
#     }
    
#     return render(request, 'hospital/bed_occupancy_reports.html', context)


# @login_required
# def export_occupancy_report(request):
#     """Export occupancy data as CSV"""
#     import csv
#     from django.http import HttpResponse
    
#     # Check authorization
#     if not request.user.profile.is_approved or request.user.profile.role != 'hospital_staff':
#         return redirect('home')
    
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="bed_occupancy_report.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['Ward', 'Total Beds', 'Occupied', 'Available', 'Occupancy Rate (%)'])
    
#     for ward in Ward.objects.all():
#         ward_beds = Bed.objects.filter(ward=ward, is_operational=True)
#         total = ward_beds.count()
#         occupied = ward_beds.filter(is_occupied=True).count()
#         available = ward_beds.filter(is_occupied=False).count()
#         occupancy_rate = (occupied / total * 100) if total > 0 else 0
        
#         writer.writerow([
#             ward.name,
#             total,
#             occupied,
#             available,
#             f"{occupancy_rate:.1f}"
#         ])
    
#     return response

# # optiona but useful - add view to see bed logs
# # @login_required
# # def bed_status_logs(request):
# #     """View all bed status change logs"""
# #     if not request.user.profile.is_approved:
# #         return redirect('home')
    
# #     # Only IT Support and Hospital Staff can view logs
# #     if request.user.profile.role not in ['it_support', 'hospital_staff']:
# #         return redirect('home')
    
# #     # Get filter parameters
# #     bed_filter = request.GET.get('bed', '')
# #     date_from = request.GET.get('date_from', '')
# #     date_to = request.GET.get('date_to', '')
    
# #     # Base query
# #     logs = BedStatusLog.objects.select_related('bed', 'bed__ward', 'patient', 'changed_by').all()
    
# #     # Apply filters
# #     if bed_filter:
# #         logs = logs.filter(bed__id=bed_filter)
    
# #     if date_from:
# #         logs = logs.filter(changed_at__gte=date_from)
    
# #     if date_to:
# #         from datetime import datetime, timedelta
# #         date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
# #         logs = logs.filter(changed_at__lt=date_to_obj)
    
# #     # Order by most recent
# #     logs = logs.order_by('-changed_at')[:100]  # Limit to 100 most recent
    
# #     # Get all beds for filter dropdown
# #     beds = Bed.objects.select_related('ward').all()
    
# #     context = {
# #         'logs': logs,
# #         'beds': beds,
# #         'bed_filter': bed_filter,
# #         'date_from': date_from,
# #         'date_to': date_to,
# #         'total_logs': logs.count(),
# #     }
    
# #     return render(request, 'hospital/bed_status_logs.html', context)

# @login_required
# def discharge_alerts(request):
#     """Show patients due for discharge soon - helps prepare discharge process"""
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     # Nurses and Hospital Staff can view
#     if request.user.profile.role not in ['nurse', 'hospital_staff']:
#         return redirect('home')
    
#     from datetime import date, timedelta
    
#     today = date.today()
#     tomorrow = today + timedelta(days=1)
#     day_after_tomorrow = today + timedelta(days=2)
    
#     # Patients due TODAY (URGENT)
#     due_today = PatientAdmission.objects.filter(
#         status='admitted',
#         predicted_discharge_date=today
#     ).select_related('bed', 'bed__ward', 'assigned_by').order_by('bed__ward__name', 'bed__bed_number')
    
#     # Patients due TOMORROW
#     due_tomorrow = PatientAdmission.objects.filter(
#         status='admitted',
#         predicted_discharge_date=tomorrow
#     ).select_related('bed', 'bed__ward', 'assigned_by').order_by('bed__ward__name', 'bed__bed_number')
    
#     # Patients due in 2 DAYS
#     due_in_2_days = PatientAdmission.objects.filter(
#         status='admitted',
#         predicted_discharge_date=day_after_tomorrow
#     ).select_related('bed', 'bed__ward', 'assigned_by').order_by('bed__ward__name', 'bed__bed_number')
    
#     # OVERDUE patients (predicted discharge date passed but still admitted)
#     overdue = PatientAdmission.objects.filter(
#         status='admitted',
#         predicted_discharge_date__lt=today
#     ).select_related('bed', 'bed__ward', 'assigned_by').order_by('predicted_discharge_date')
    
#     # Calculate stats
#     total_alerts = due_today.count() + due_tomorrow.count() + overdue.count()
    
#     # Next 7 days summary
#     next_7_days_summary = []
#     for i in range(7):
#         forecast_date = today + timedelta(days=i)
#         count = PatientAdmission.objects.filter(
#             status='admitted',
#             predicted_discharge_date=forecast_date
#         ).count()
        
#         next_7_days_summary.append({
#             'date': forecast_date,
#             'day_name': forecast_date.strftime('%A'),
#             'count': count,
#             'is_today': (i == 0),
#             'is_tomorrow': (i == 1),
#         })
    
#     context = {
#         'due_today': due_today,
#         'due_tomorrow': due_tomorrow,
#         'due_in_2_days': due_in_2_days,
#         'overdue': overdue,
#         'total_alerts': total_alerts,
#         'next_7_days_summary': next_7_days_summary,
#         'today': today,
#     }
    
#     return render(request, 'hospital/discharge_alerts.html', context)

# @login_required
# def bed_availability_forecast(request):
#     """Show when beds will become available based on predicted discharge dates"""
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     # All roles can view this (nurses, hospital staff)
#     if request.user.profile.role not in ['nurse', 'hospital_staff']:
#         return redirect('home')
    
#     from datetime import date, timedelta
    
#     # Get all admitted patients with predicted discharge dates
#     upcoming_discharges = []
    
#     for admission in PatientAdmission.objects.filter(status='admitted').select_related('bed', 'bed__ward'):
#         if admission.predicted_discharge_date:
#             days_until = (admission.predicted_discharge_date - date.today()).days
            
#             upcoming_discharges.append({
#                 'patient': admission,
#                 'bed': admission.bed,
#                 'ward': admission.bed.ward,
#                 'predicted_discharge': admission.predicted_discharge_date,
#                 'days_until': days_until,
#                 'admitted_on': admission.admission_date,
#                 'predicted_los': admission.predicted_los,
#             })
    
#     # Sort by discharge date (soonest first)
#     upcoming_discharges.sort(key=lambda x: x['predicted_discharge'])
    
#     # Group by date
#     forecast_by_date = {}
#     for discharge in upcoming_discharges:
#         discharge_date = discharge['predicted_discharge']
#         if discharge_date not in forecast_by_date:
#             forecast_by_date[discharge_date] = []
#         forecast_by_date[discharge_date].append(discharge)
    
#     # Next 7 days forecast
#     today = date.today()
#     next_7_days = []
    
#     for i in range(7):
#         forecast_date = today + timedelta(days=i)
#         beds_freeing = len(forecast_by_date.get(forecast_date, []))
        
#         next_7_days.append({
#             'date': forecast_date,
#             'day_name': forecast_date.strftime('%A'),
#             'beds_freeing': beds_freeing,
#             'discharges': forecast_by_date.get(forecast_date, []),
#             'is_today': (i == 0),
#             'is_tomorrow': (i == 1),
#         })
    
#     # Calculate total available beds if all predictions are accurate
#     current_available = Bed.objects.filter(is_occupied=False, is_operational=True).count()
#     total_beds = Bed.objects.filter(is_operational=True).count()
#     current_occupied = Bed.objects.filter(is_occupied=True, is_operational=True).count()
    
#     # Group by ward
#     ward_forecast = {}
#     for discharge in upcoming_discharges:
#         ward_name = discharge['ward'].name
#         if ward_name not in ward_forecast:
#             ward_forecast[ward_name] = []
#         ward_forecast[ward_name].append(discharge)
    
#     context = {
#         'upcoming_discharges': upcoming_discharges[:30],  # Show next 30
#         'next_7_days': next_7_days,
#         'current_available': current_available,
#         'current_occupied': current_occupied,
#         'total_beds': total_beds,
#         'forecast_by_date': forecast_by_date,
#         'ward_forecast': ward_forecast,
#         'today': today,
#     }
    
#     return render(request, 'hospital/bed_availability_forecast.html', context)

# @login_required
# def dashboard(request):
#     """Main overview dashboard for all users"""
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     from datetime import date, timedelta
#     from django.db.models import Count
    
#     today = date.today()
    
#     # === OVERALL STATS ===
#     total_beds = Bed.objects.filter(is_operational=True).count()
#     occupied_beds = Bed.objects.filter(is_occupied=True, is_operational=True).count()
#     available_beds = total_beds - occupied_beds
#     occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0
    
#     current_patients = PatientAdmission.objects.filter(status='admitted').count()
    
#     # Discharges today
#     discharges_today = PatientAdmission.objects.filter(
#         status='admitted',
#         predicted_discharge_date=today
#     ).count()
    
#     # Discharges this week
#     week_end = today + timedelta(days=7)
#     discharges_this_week = PatientAdmission.objects.filter(
#         status='admitted',
#         predicted_discharge_date__gte=today,
#         predicted_discharge_date__lte=week_end
#     ).count()
    
#     # Overdue discharges
#     overdue_discharges = PatientAdmission.objects.filter(
#         status='admitted',
#         predicted_discharge_date__lt=today
#     ).count()
    
#     # === WARD BREAKDOWN ===
#     ward_stats = []
#     for ward in Ward.objects.all():
#         ward_beds = Bed.objects.filter(ward=ward, is_operational=True)
#         ward_occupied = ward_beds.filter(is_occupied=True).count()
#         ward_total = ward_beds.count()
#         ward_available = ward_total - ward_occupied
#         ward_occupancy = (ward_occupied / ward_total * 100) if ward_total > 0 else 0
        
#         ward_stats.append({
#             'name': ward.name,
#             'occupied': ward_occupied,
#             'available': ward_available,
#             'total': ward_total,
#             'occupancy_rate': round(ward_occupancy, 1)
#         })
    
#     # === RECENT ACTIVITY ===
#     recent_admissions = PatientAdmission.objects.filter(
#         status='admitted'
#     ).order_by('-admission_date')[:5]
    
#     recent_discharges = PatientAdmission.objects.filter(
#         status='discharged'
#     ).order_by('-actual_discharge_date')[:5]
    
#     # === NEXT 7 DAYS FORECAST ===
#     forecast_7_days = []
#     for i in range(7):
#         forecast_date = today + timedelta(days=i)
#         count = PatientAdmission.objects.filter(
#             status='admitted',
#             predicted_discharge_date=forecast_date
#         ).count()
        
#         forecast_7_days.append({
#             'date': forecast_date,
#             'day': forecast_date.strftime('%a'),
#             'count': count,
#             'is_today': (i == 0)
#         })
    
#     # === ALERTS ===
#     alerts = []
    
#     if overdue_discharges > 0:
#         alerts.append({
#             'type': 'danger',
#             'icon': '⚠️',
#             'message': f'{overdue_discharges} overdue discharge(s) need attention'
#         })
    
#     if available_beds < 5:
#         alerts.append({
#             'type': 'warning',
#             'icon': '🛏️',
#             'message': f'Low bed availability: Only {available_beds} beds free'
#         })
    
#     if discharges_today > 0:
#         alerts.append({
#             'type': 'info',
#             'icon': '📋',
#             'message': f'{discharges_today} discharge(s) scheduled for today'
#         })
    
#     context = {
#         'total_beds': total_beds,
#         'occupied_beds': occupied_beds,
#         'available_beds': available_beds,
#         'occupancy_rate': round(occupancy_rate, 1),
#         'current_patients': current_patients,
#         'discharges_today': discharges_today,
#         'discharges_this_week': discharges_this_week,
#         'overdue_discharges': overdue_discharges,
#         'ward_stats': ward_stats,
#         'recent_admissions': recent_admissions,
#         'recent_discharges': recent_discharges,
#         'forecast_7_days': forecast_7_days,
#         'alerts': alerts,
#         'user_role': request.user.profile.role,
#     }
    
#     return render(request, 'hospital/dashboard.html', context)


# Dashboard as the Landing Page
import os
import joblib
import pandas as pd
import numpy as np
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db import models  # Add this line with other imports
from .models import Profile, Ward, Bed, PatientAdmission
from datetime import date, timedelta

# --- 1. Load ML artifacts ---
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models')

# These load when the server starts
model = joblib.load(os.path.join(MODEL_PATH, 'best_model.pkl'))
scaler = joblib.load(os.path.join(MODEL_PATH, 'scaler.pkl'))
feature_names = joblib.load(os.path.join(MODEL_PATH, 'feature_names.pkl'))

# Comorbidity field names
COMORBIDITY_FIELDS = [
    'dialysisrenalendstage', 'asthma', 'irondef', 'pneum',
    'substancedependence', 'psychologicaldisordermajor',
    'depress', 'psychother', 'fibrosisandother', 'malnutrition', 'hemo'
]

# --- 2. Home View ---
@login_required
def home(request):
    # Check if user is approved
    if not request.user.profile.is_approved:
        return render(request, 'hospital/pending.html')
    
    return redirect('dashboard')

# # Option 2: OR keep simple home pages
# @login_required
# def home(request):
#     """Main entry point - shows simple home pages"""
#     if not request.user.profile.is_approved:
#         return render(request, 'hospital/pending.html')
    
#     # Show role-specific simple home page
#     role = request.user.profile.role
#     if role == 'nurse':
#         return render(request, 'hospital/nurse_home.html')
#     elif role == 'hospital_staff':
#         return render(request, 'hospital/staff_home.html')
#     elif role == 'it_support':
#         return render(request, 'hospital/it_home.html')
#     else:
#         return render(request, 'hospital/home.html')
    
@login_required
def dashboard(request):
    """Main overview dashboard for all users"""
    if not request.user.profile.is_approved:
        return redirect('home')
    
    from datetime import date, timedelta
    from django.db.models import Count
    
    today = date.today()
    
    # === OVERALL STATS ===
    total_beds = Bed.objects.filter(is_operational=True).count()
    occupied_beds = Bed.objects.filter(is_occupied=True, is_operational=True).count()
    available_beds = total_beds - occupied_beds
    occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0
    
    current_patients = PatientAdmission.objects.filter(status='admitted').count()
    
    # Discharges today
    discharges_today = PatientAdmission.objects.filter(
        status='admitted',
        predicted_discharge_date=today
    ).count()
    
    # Discharges this week
    week_end = today + timedelta(days=7)
    discharges_this_week = PatientAdmission.objects.filter(
        status='admitted',
        predicted_discharge_date__gte=today,
        predicted_discharge_date__lte=week_end
    ).count()
    
    # Overdue discharges
    overdue_discharges = PatientAdmission.objects.filter(
        status='admitted',
        predicted_discharge_date__lt=today
    ).count()
    
    # === WARD BREAKDOWN ===
    ward_stats = []
    for ward in Ward.objects.all():
        ward_beds = Bed.objects.filter(ward=ward, is_operational=True)
        ward_occupied = ward_beds.filter(is_occupied=True).count()
        ward_total = ward_beds.count()
        ward_available = ward_total - ward_occupied
        ward_occupancy = (ward_occupied / ward_total * 100) if ward_total > 0 else 0
        
        ward_stats.append({
            'name': ward.name,
            'occupied': ward_occupied,
            'available': ward_available,
            'total': ward_total,
            'occupancy_rate': round(ward_occupancy, 1)
        })
    
    # === RECENT ACTIVITY ===
    recent_admissions = PatientAdmission.objects.filter(
        status='admitted'
    ).order_by('-admission_date')[:5]
    
    recent_discharges = PatientAdmission.objects.filter(
        status='discharged'
    ).order_by('-actual_discharge_date')[:5]
    
    # === NEXT 7 DAYS FORECAST ===
    forecast_7_days = []
    for i in range(7):
        forecast_date = today + timedelta(days=i)
        count = PatientAdmission.objects.filter(
            status='admitted',
            predicted_discharge_date=forecast_date
        ).count()
        
        forecast_7_days.append({
            'date': forecast_date,
            'day': forecast_date.strftime('%a'),
            'count': count,
            'is_today': (i == 0)
        })
    
    # === ALERTS ===
    alerts = []
    
    if overdue_discharges > 0:
        alerts.append({
            'type': 'danger',
            'icon': '⚠️',
            'message': f'{overdue_discharges} overdue discharge(s) need attention'
        })
    
    if available_beds < 5:
        alerts.append({
            'type': 'warning',
            'icon': '🛏️',
            'message': f'Low bed availability: Only {available_beds} beds free'
        })
    
    if discharges_today > 0:
        alerts.append({
            'type': 'info',
            'icon': '📋',
            'message': f'{discharges_today} discharge(s) scheduled for today'
        })
    
    context = {
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'occupancy_rate': round(occupancy_rate, 1),
        'current_patients': current_patients,
        'discharges_today': discharges_today,
        'discharges_this_week': discharges_this_week,
        'overdue_discharges': overdue_discharges,
        'ward_stats': ward_stats,
        'recent_admissions': recent_admissions,
        'recent_discharges': recent_discharges,
        'forecast_7_days': forecast_7_days,
        'alerts': alerts,
        'user_role': request.user.profile.role,
    }
    
    return render(request, 'hospital/dashboard.html', context)


# --- 3. Signup View ---
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile with pending status
            Profile.objects.create(
                user=user,
                role='pending',
                is_approved=False
            )
            return redirect('signup_success')
    else:
        form = UserCreationForm()
    return render(request, 'hospital/signup.html', {'form': form})

# --- 4. Signup Success View ---
def signup_success(request):
    return render(request, 'hospital/signup_success.html')

# --- 5. Enhanced Prediction View ---
@login_required
def predict(request):
    # Check approval status first
    if not request.user.profile.is_approved:
        return redirect('home')
    
    # Then check role
    if request.user.profile.role != 'nurse':
        return redirect('home')

    prediction_result = None
    comorbidity_count = 0
    rcount = 0
    risk_score = 0
    
    if request.method == 'POST':
        try:
            # 1. Capture Raw Inputs from HTML
            raw_input = {
                'gender': 1 if request.POST.get('gender') == 'Male' else 0,
                'rcount': int(request.POST.get('rcount', 0)),
                'bmi': float(request.POST.get('bmi', 25.0)),
                'pulse': float(request.POST.get('pulse', 75)),
                'respiration': float(request.POST.get('respiration', 16.0)),
                'hematocrit': float(request.POST.get('hematocrit', 40.0)),
                'neutrophils': float(request.POST.get('neutrophils', 4.0)),
                'glucose': float(request.POST.get('glucose', 100)),
                'sodium': float(request.POST.get('sodium', 140)),
                'creatinine': float(request.POST.get('creatinine', 1.0)),
                'bloodureanitro': float(request.POST.get('bloodureanitro', 12.0)),
                'facility': request.POST.get('facility', 'A'),
                'admission_month': int(request.POST.get('admission_month', 1)),
                'admission_dayofweek': int(request.POST.get('admission_dayofweek', 0)),
                'secondarydiagnosisnonicd9': int(request.POST.get('secondarydiagnosisnonicd9', 1))
            }
            
            # Capture comorbidities
            comorbidities = {}
            for field in COMORBIDITY_FIELDS:
                comorbidities[field] = 1 if request.POST.get(field) else 0
            
            # Count comorbidities
            comorbidity_count = sum(comorbidities.values())
            rcount = raw_input['rcount']

            # 2. Create DataFrame with all 42 columns
            df = pd.DataFrame(0, index=[0], columns=feature_names)

            # 3. Fill basic columns
            for col in raw_input:
                if col in df.columns:
                    df[col] = raw_input[col]
            
            # 4. Fill comorbidity columns
            for field, value in comorbidities.items():
                if field in df.columns:
                    df[field] = value

            # 5. Feature Engineering
            df['total_comorbidities'] = comorbidity_count
            df['high_glucose'] = int(raw_input['glucose'] > 140)
            df['low_sodium'] = int(raw_input['sodium'] < 135)
            df['high_creatinine'] = int(raw_input['creatinine'] > 1.3)
            df['low_bmi'] = int(raw_input['bmi'] < 18.5)
            df['high_bmi'] = int(raw_input['bmi'] > 30)
            df['abnormal_vitals'] = (
                int(raw_input['pulse'] < 60 or raw_input['pulse'] > 100) +
                int(raw_input['respiration'] < 12 or raw_input['respiration'] > 20)
            )
            
            # Admission quarter
            df['admission_quarter'] = (raw_input['admission_month'] - 1) // 3 + 1
            
            # Facility one-hot encoding
            facility_col = f"facility_{raw_input['facility']}"
            if facility_col in df.columns:
                df[facility_col] = 1

            # 6. Scale and Predict
            input_scaled = scaler.transform(df)
            prediction = model.predict(input_scaled)[0]
            prediction_result = round(prediction, 1)
            
            # 7. Calculate risk score
            risk_score = min((comorbidity_count * 10) + (rcount * 15), 100)

        except Exception as e:
            prediction_result = None
            print(f"Prediction Error: {e}")  # For debugging

    context = {
        'prediction': prediction_result,
        'comorbidity_count': comorbidity_count,
        'rcount': rcount,
        'risk_score': risk_score,
    }
    
    return render(request, 'hospital/predict.html', context)

# Add to your existing views.py (after predict function)

@login_required
def ward_availability(request):
    # Check approval and role
    if not request.user.profile.is_approved:
        return redirect('home')
    
    if request.user.profile.role != 'nurse':
        return redirect('home')
    
    # Get all wards with stats
    wards = Ward.objects.all()
    
    ward_stats = []
    for ward in wards:
        operational_beds = Bed.objects.filter(ward=ward, is_operational=True).count()
        occupied = Bed.objects.filter(ward=ward, is_occupied=True, is_operational=True).count()
        available = operational_beds - occupied
        occupancy_rate = (occupied / operational_beds * 100) if operational_beds > 0 else 0
        
        # Determine status color
        if available == 0:
            status = 'full'
            status_color = '#ef4444'  # red
        elif occupancy_rate > 80:
            status = 'almost_full'
            status_color = '#f59e0b'  # orange
        else:
            status = 'available'
            status_color = '#10b981'  # green
        
        ward_stats.append({
            'id': ward.id,
            'name': ward.name,
            'type': ward.get_ward_type_display(),
            'floor': ward.floor,
            'total': operational_beds,
            'occupied': occupied,
            'available': available,
            'occupancy_rate': round(occupancy_rate, 1),
            'status': status,
            'status_color': status_color,
        })
    
    context = {'ward_stats': ward_stats}
    return render(request, 'hospital/ward_availability.html', context)

# Add after ward_availability function

@login_required
def assign_bed(request):
    # Check approval and role
    if not request.user.profile.is_approved:
        return redirect('home')
    
    if request.user.profile.role != 'nurse':
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Get form data
            patient_name = request.POST.get('patient_name')
            patient_id = request.POST.get('patient_id')
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            bed_id = request.POST.get('bed_id')
            predicted_los = request.POST.get('predicted_los')
            notes = request.POST.get('notes', '')
            
            # Get the bed
            bed = Bed.objects.get(id=bed_id)
            
            # Check if bed is available
            if bed.is_occupied:
                messages.error(request, f"Bed {bed.bed_number} is already occupied!")
                return redirect('assign_bed')
            
            # Calculate predicted discharge date
            predicted_discharge = None
            if predicted_los:
                from datetime import timedelta, date
                predicted_discharge = date.today() + timedelta(days=float(predicted_los))
            
            # Create patient admission
            admission = PatientAdmission.objects.create(
                patient_name=patient_name,
                patient_id=patient_id,
                age=int(age) if age else None,
                gender=gender,
                bed=bed,
                predicted_los=float(predicted_los) if predicted_los else None,
                predicted_discharge_date=predicted_discharge,
                assigned_by=request.user,
                notes=notes,
                status='admitted'
            )
            
            # Mark bed as occupied
            bed.is_occupied = True
            bed.save()
            
            messages.success(request, f"Patient {patient_name} successfully assigned to Bed {bed.bed_number}")
            return redirect('assign_bed')
            
        except Bed.DoesNotExist:
            messages.error(request, "Selected bed not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect('assign_bed')
    
    # GET request - show form
    # Get all wards with available beds
    wards = Ward.objects.all()
    
    # Get available beds grouped by ward
    ward_beds = []
    for ward in wards:
        available_beds = Bed.objects.filter(
            ward=ward, 
            is_occupied=False, 
            is_operational=True
        )
        
        if available_beds.exists():
            ward_beds.append({
                'ward': ward,
                'beds': available_beds
            })
    
    # Get recent admissions
    recent_admissions = PatientAdmission.objects.filter(
        status='admitted'
    ).select_related('bed', 'bed__ward', 'assigned_by').order_by('-admission_date')[:10]
    
    context = {
        'ward_beds': ward_beds,
        'recent_admissions': recent_admissions,
    }
    
    return render(request, 'hospital/assign_bed.html', context)

from datetime import date, timedelta

@login_required
def assign_bed_with_prediction(request):
    """Assign patient to bed with pre-filled prediction data"""
    if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
        return redirect('home')
    
    if request.method == 'POST':
        # Get prediction data from previous form
        predicted_los = request.POST.get('predicted_los')
        comorbidity_count = request.POST.get('comorbidity_count')
        risk_score = request.POST.get('risk_score')
        
        # Check for available beds
        wards = Ward.objects.all()
        ward_beds = []
        
        for ward in wards:
            available_beds = Bed.objects.filter(
                ward=ward, 
                is_occupied=False, 
                is_operational=True
            )
            
            if available_beds.exists():
                ward_beds.append({
                    'ward': ward,
                    'beds': available_beds
                })
        
        # If no beds available, show special message
        if not ward_beds:
            # Get stats for no-beds message
            total_beds = Bed.objects.filter(is_operational=True).count()
            occupied_beds = Bed.objects.filter(is_occupied=True, is_operational=True).count()
            
            # Find patients near discharge (within 2 days)
            near_discharge = []
            for admission in PatientAdmission.objects.filter(status='admitted').select_related('bed', 'bed__ward'):
                if admission.predicted_discharge_date:
                    days_until = (admission.predicted_discharge_date - date.today()).days
                    if days_until <= 2:
                        near_discharge.append({
                            'admission': admission,
                            'days_until': days_until
                        })
            
            context = {
                'no_beds_available': True,
                'total_beds': total_beds,
                'occupied_beds': occupied_beds,
                'near_discharge': near_discharge,
                'predicted_los': predicted_los,
            }
            return render(request, 'hospital/assign_bed_with_prediction.html', context)
        
        # Beds available - show normal assignment form with pre-filled data
        recent_admissions = PatientAdmission.objects.filter(
            status='admitted'
        ).select_related('bed', 'bed__ward', 'assigned_by').order_by('-admission_date')[:10]
        
        context = {
            'ward_beds': ward_beds,
            'recent_admissions': recent_admissions,
            'predicted_los': predicted_los,
            'comorbidity_count': comorbidity_count,
            'risk_score': risk_score,
            'from_prediction': True,
        }
        
        return render(request, 'hospital/assign_bed_with_prediction.html', context)
    
    # GET request - redirect to normal predict page
    return redirect('predict')

# @login_required
# def process_bed_assignment(request):
#     """Process the actual bed assignment"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     if request.method == 'POST':
#         try:
#             # Get form data - NO patient_id needed!
#             patient_name = request.POST.get('patient_name')
#             age = request.POST.get('age')
#             gender = request.POST.get('gender')
#             bed_id = request.POST.get('bed_id')
#             predicted_los = request.POST.get('predicted_los')
#             notes = request.POST.get('notes', '')
            
#             # Get the bed
#             bed = Bed.objects.get(id=bed_id)
            
#             # Check if bed is available
#             if bed.is_occupied:
#                 messages.error(request, f"Bed {bed.bed_number} is already occupied!")
#                 return redirect('assign_bed')
            
#             # Calculate predicted discharge date
#             predicted_discharge = None
#             if predicted_los:
#                 from datetime import date, timedelta
#                 predicted_discharge = date.today() + timedelta(days=float(predicted_los))
            
#             # Create patient admission - patient_id auto-generated!
#             admission = PatientAdmission.objects.create(
#                 patient_name=patient_name,
#                 # patient_id will be auto-generated by the model
#                 age=int(age) if age else None,
#                 gender=gender,
#                 bed=bed,
#                 predicted_los=float(predicted_los) if predicted_los else None,
#                 predicted_discharge_date=predicted_discharge,
#                 assigned_by=request.user,
#                 notes=notes,
#                 status='admitted'
#             )
            
#             # Mark bed as occupied
#             bed.is_occupied = True
#             bed.save()
            
#             messages.success(request, f"✅ Patient {patient_name} (ID: {admission.patient_id}) successfully assigned to Bed {bed.bed_number}. Predicted discharge: {predicted_discharge.strftime('%b %d, %Y') if predicted_discharge else 'N/A'}")
#             return redirect('view_patients')
            
#         except Bed.DoesNotExist:
#             messages.error(request, "Selected bed not found")
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
        
#         return redirect('assign_bed')
    
#     return redirect('assign_bed')

# @login_required
# def process_bed_assignment(request):
#     """Process the actual bed assignment"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     if request.method == 'POST':
#         try:
#             # Get form data
#             patient_name = request.POST.get('patient_name')
#             age = request.POST.get('age')
#             gender = request.POST.get('gender')
#             bed_id = request.POST.get('bed_id')
#             predicted_los = request.POST.get('predicted_los')
#             notes = request.POST.get('notes', '')
            
#             # Get the bed
#             bed = Bed.objects.get(id=bed_id)
            
#             # Check if bed is available
#             if bed.is_occupied:
#                 messages.error(request, f"Bed {bed.bed_number} is already occupied!")
#                 return redirect('assign_bed')
            
#             # Calculate predicted discharge date
#             predicted_discharge = None
#             if predicted_los:
#                 from datetime import date, timedelta
#                 predicted_discharge = date.today() + timedelta(days=float(predicted_los))
            
#             # Create patient admission
#             admission = PatientAdmission.objects.create(
#                 patient_name=patient_name,
#                 age=int(age) if age else None,
#                 gender=gender,
#                 bed=bed,
#                 predicted_los=float(predicted_los) if predicted_los else None,
#                 predicted_discharge_date=predicted_discharge,
#                 assigned_by=request.user,
#                 notes=notes,
#                 status='admitted'
#             )
            
#             # Mark bed as occupied
#             previous_status = 'available' if not bed.is_occupied else 'occupied'
#             bed.is_occupied = True
#             bed.save()
            
#             # # ⭐ NEW: Log the bed status change
#             # BedStatusLog.objects.create(
#             #     bed=bed,
#             #     patient=admission,
#             #     previous_status=previous_status,
#             #     new_status='occupied',
#             #     changed_by=request.user,
#             #     reason='patient_admission',
#             #     notes=f"Patient {patient_name} (ID: {admission.patient_id}) admitted"
#             # )
            
#             messages.success(request, f"✅ Patient {patient_name} (ID: {admission.patient_id}) successfully assigned to Bed {bed.bed_number}. Predicted discharge: {predicted_discharge.strftime('%b %d, %Y') if predicted_discharge else 'N/A'}")
#             return redirect('view_patients')
            
#         except Bed.DoesNotExist:
#             messages.error(request, "Selected bed not found")
#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
        
#         return redirect('assign_bed')
    
#     return redirect('assign_bed')

@login_required
def process_bed_assignment(request):
    """Process the actual bed assignment"""
    if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Get basic form data
            patient_name = request.POST.get('patient_name')
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            bed_id = request.POST.get('bed_id')
            predicted_los = request.POST.get('predicted_los')
            notes = request.POST.get('notes', '')
            
            # ⭐ NEW: Get additional patient information
            contact_number = request.POST.get('contact_number', '')
            blood_group = request.POST.get('blood_group', '')
            date_of_birth = request.POST.get('date_of_birth', '')
            marital_status = request.POST.get('marital_status', '')
            nationality = request.POST.get('nationality', '')
            known_allergies = request.POST.get('known_allergies', '')
            occupation = request.POST.get('occupation', '')
            
            # Get the bed
            bed = Bed.objects.get(id=bed_id)
            
            # Check if bed is available
            if bed.is_occupied:
                messages.error(request, f"Bed {bed.bed_number} is already occupied!")
                return redirect('assign_bed')
            
            # Calculate predicted discharge date
            predicted_discharge = None
            if predicted_los:
                from datetime import date, timedelta
                predicted_discharge = date.today() + timedelta(days=float(predicted_los))
            
            # ⭐ UPDATED: Create patient admission with new fields
            admission = PatientAdmission.objects.create(
                patient_name=patient_name,
                age=int(age) if age else None,
                gender=gender,
                bed=bed,
                predicted_los=float(predicted_los) if predicted_los else None,
                predicted_discharge_date=predicted_discharge,
                assigned_by=request.user,
                notes=notes,
                status='admitted',
                # New fields
                contact_number=contact_number,
                blood_group=blood_group,
                date_of_birth=date_of_birth if date_of_birth else None,
                marital_status=marital_status,
                nationality=nationality,
                known_allergies=known_allergies,
                occupation=occupation,
            )
            
            # Mark bed as occupied
            previous_status = 'available' if not bed.is_occupied else 'occupied'
            bed.is_occupied = True
            bed.save()
            
            messages.success(request, f"✅ Patient {patient_name} (ID: {admission.patient_id}) successfully assigned to Bed {bed.bed_number}. Predicted discharge: {predicted_discharge.strftime('%b %d, %Y') if predicted_discharge else 'N/A'}")
            return redirect('view_patients')
            
        except Bed.DoesNotExist:
            messages.error(request, "Selected bed not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect('assign_bed')
    
    return redirect('assign_bed')

# @login_required
# def discharge_patient(request, admission_id):
#     """Discharge a patient and free up their bed"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
    
#     try:
#         admission = PatientAdmission.objects.get(id=admission_id, status='admitted')
        
#         if request.method == 'POST':
#             # Mark patient as discharged
#             admission.status = 'discharged'
#             admission.actual_discharge_date = timezone.now()
#             admission.save()
            
#             # Free up the bed
#             if admission.bed:
#                 admission.bed.is_occupied = False
#                 admission.bed.save()
            
#             messages.success(request, f"Patient {admission.patient_name} discharged successfully. Bed {admission.bed.bed_number} is now available.")
#             return redirect('view_patients')
        
#         # GET - show confirmation page
#         context = {
#             'admission': admission,
#         }
#         return render(request, 'hospital/discharge_confirm.html', context)
        
#     except PatientAdmission.DoesNotExist:
#         messages.error(request, "Patient not found or already discharged")
#         return redirect('view_patients')

@login_required
def discharge_patient(request, admission_id):
    """Discharge a patient and free up their bed"""
    if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
        return redirect('home')
    
    try:
        admission = PatientAdmission.objects.get(id=admission_id, status='admitted')
        
        if request.method == 'POST':
            # Mark patient as discharged
            admission.status = 'discharged'
            admission.actual_discharge_date = timezone.now()
            admission.save()
            
            # Free up the bed
            if admission.bed:
                bed = admission.bed
                bed.is_occupied = False
                bed.save()
                
                # ⭐ NEW: Log the bed status change
                # BedStatusLog.objects.create(
                #     bed=bed,
                #     patient=admission,
                #     previous_status='occupied',
                #     new_status='available',
                #     changed_by=request.user,
                #     reason='patient_discharge',
                #     notes=f"Patient {admission.patient_name} (ID: {admission.patient_id}) discharged"
                # )
            
            messages.success(request, f"Patient {admission.patient_name} discharged successfully. Bed {admission.bed.bed_number} is now available.")
            return redirect('view_patients')
        
        # GET - show confirmation page
        context = {
            'admission': admission,
        }
        return render(request, 'hospital/discharge_confirm.html', context)
        
    except PatientAdmission.DoesNotExist:
        messages.error(request, "Patient not found or already discharged")
        return redirect('view_patients')

# @login_required
# def view_patients(request):
#     """View all admitted patients"""
#     if not request.user.profile.is_approved or request.user.profile.role != 'nurse':
#         return redirect('home')
@login_required
def view_patients(request):
    """View all admitted patients"""
    if not request.user.profile.is_approved:
        return redirect('home')
    
    # Allow both nurses AND hospital staff to view patients
    if request.user.profile.role not in ['nurse', 'hospital_staff']:
        return redirect('home')
    
    # Get filter parameters
    ward_filter = request.GET.get('ward', '')
    search_query = request.GET.get('search', '')
    
    # Base query - only admitted patients
    patients = PatientAdmission.objects.filter(status='admitted').select_related('bed', 'bed__ward', 'assigned_by')
    
    # Apply filters
    if ward_filter:
        patients = patients.filter(bed__ward__id=ward_filter)
    
    if search_query:
        patients = patients.filter(
            models.Q(patient_name__icontains=search_query) |
            models.Q(patient_id__icontains=search_query)
        )
    
    # Order by most recent first
    patients = patients.order_by('-admission_date')
    
    # Get all wards for filter dropdown
    wards = Ward.objects.all()
    
    # Calculate stats
    total_patients = patients.count()
    
    context = {
        'patients': patients,
        'wards': wards,
        'total_patients': total_patients,
        'ward_filter': ward_filter,
        'search_query': search_query,
    }
    
    return render(request, 'hospital/view_patients.html', context)

@login_required
def discharge_history(request):
    """View all discharged patients with stats"""
    if not request.user.profile.is_approved:
        return redirect('home')
    
    # Only nurses and hospital_staff can view
    if request.user.profile.role not in ['nurse', 'hospital_staff']:
        return redirect('home')
    
    # Get filter parameters
    ward_filter = request.GET.get('ward', '')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base query - only discharged patients
    discharges = PatientAdmission.objects.filter(status='discharged').select_related('bed', 'bed__ward', 'assigned_by')
    
    # Apply filters
    if ward_filter:
        discharges = discharges.filter(bed__ward__id=ward_filter)
    
    if search_query:
        discharges = discharges.filter(
            models.Q(patient_name__icontains=search_query) |
            models.Q(patient_id__icontains=search_query)
        )
    
    if date_from:
        discharges = discharges.filter(actual_discharge_date__gte=date_from)
    
    if date_to:
        from datetime import datetime, timedelta
        # Add one day to include the entire end date
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        discharges = discharges.filter(actual_discharge_date__lt=date_to_obj)
    
    # Order by most recent discharge first
    discharges = discharges.order_by('-actual_discharge_date')
    
    # Calculate actual length of stay for each discharge
    discharge_data = []
    total_predicted_error = 0
    predictions_count = 0
    
    for discharge in discharges:
        if discharge.admission_date and discharge.actual_discharge_date:
            # Calculate actual LoS in days
            actual_los = (discharge.actual_discharge_date - discharge.admission_date).total_seconds() / 86400
            actual_los = round(actual_los, 1)
            
            # Calculate prediction error if predicted LoS exists
            prediction_error = None
            accuracy_class = ''
            
            if discharge.predicted_los:
                prediction_error = actual_los - discharge.predicted_los
                total_predicted_error += abs(prediction_error)
                predictions_count += 1
                
                # Classify accuracy
                if abs(prediction_error) <= 0.5:
                    accuracy_class = 'excellent'  # Green
                elif abs(prediction_error) <= 1.5:
                    accuracy_class = 'good'  # Yellow
                else:
                    accuracy_class = 'poor'  # Red
            
            discharge_data.append({
                'discharge': discharge,
                'actual_los': actual_los,
                'prediction_error': prediction_error,
                'accuracy_class': accuracy_class
            })
    
    # Calculate overall stats
    total_discharges = len(discharge_data)
    avg_error = round(total_predicted_error / predictions_count, 2) if predictions_count > 0 else 0
    
    # Get all wards for filter dropdown
    wards = Ward.objects.all()
    
    context = {
        'discharge_data': discharge_data,
        'wards': wards,
        'total_discharges': total_discharges,
        'avg_error': avg_error,
        'predictions_count': predictions_count,
        'ward_filter': ward_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'hospital/discharge_history.html', context)

# --- 6. User Management View (IT Support) ---
@login_required
def manage_users(request):
    # Only IT Support can access
    if not request.user.profile.is_approved or request.user.profile.role != 'it_support':
        return redirect('home')
    
    pending_users = Profile.objects.filter(is_approved=False).select_related('user')
    approved_users = Profile.objects.filter(is_approved=True).select_related('user')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        try:
            if action == 'create':
                # CREATE NEW USER
                username = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')
                role = request.POST.get('role')
                
                # Check if username exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, f"Username '{username}' already exists")
                else:
                    new_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                    Profile.objects.create(
                        user=new_user,
                        role=role,
                        is_approved=True,
                        approved_by=request.user,
                        approved_at=timezone.now()
                    )
                    messages.success(request, f"User '{username}' created successfully")
            
            elif action == 'approve':
                # APPROVE PENDING USER
                profile = Profile.objects.get(user_id=user_id)
                new_role = request.POST.get('role')
                profile.role = new_role
                profile.is_approved = True
                profile.approved_by = request.user
                profile.approved_at = timezone.now()
                profile.save()
                messages.success(request, f"User '{profile.user.username}' approved as {profile.get_role_display()}")
            
            elif action == 'edit':
                # EDIT USER (username, email, role)
                profile = Profile.objects.get(user_id=user_id)
                new_username = request.POST.get('username')
                new_email = request.POST.get('email')
                new_role = request.POST.get('role')
                
                # Update User model
                profile.user.username = new_username
                profile.user.email = new_email
                profile.user.save()
                
                # Update Profile model
                profile.role = new_role
                profile.save()
                
                messages.success(request, f"User '{new_username}' updated successfully")
            
            elif action == 'change_password':
                # CHANGE USER PASSWORD
                profile = Profile.objects.get(user_id=user_id)
                new_password = request.POST.get('new_password')
                profile.user.set_password(new_password)
                profile.user.save()
                messages.success(request, f"Password changed for '{profile.user.username}'")
            
            elif action == 'delete':
                # DELETE USER
                profile = Profile.objects.get(user_id=user_id)
                username = profile.user.username
                profile.user.delete()  # Cascade deletes profile too
                messages.success(request, f"User '{username}' deleted successfully")
            
            elif action == 'reject':
                # REJECT PENDING USER (same as delete)
                profile = Profile.objects.get(user_id=user_id)
                username = profile.user.username
                profile.user.delete()
                messages.success(request, f"User '{username}' rejected and deleted")
                
        except Profile.DoesNotExist:
            messages.error(request, "User not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect('manage_users')
    
    context = {
        'pending_users': pending_users,
        'approved_users': approved_users,
    }
    return render(request, 'hospital/manage_users.html', context)

@login_required
def manage_wards(request):
    """IT Support manages wards and beds"""
    if not request.user.profile.is_approved or request.user.profile.role != 'it_support':
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'create_ward':
                ward = Ward.objects.create(
                    name=request.POST.get('name'),
                    ward_type=request.POST.get('ward_type'),
                    floor=request.POST.get('floor') if request.POST.get('floor') else None,
                    total_beds=int(request.POST.get('total_beds')),
                    description=request.POST.get('description', '')
                )
                messages.success(request, f"Ward '{ward.name}' created successfully")
            
            elif action == 'generate_beds':
                ward_id = request.POST.get('ward_id')
                ward = Ward.objects.get(id=ward_id)
                bed_prefix = request.POST.get('bed_prefix')
                start_number = int(request.POST.get('start_number'))
                
                # Generate beds
                for i in range(ward.total_beds):
                    bed_number = f"{bed_prefix}-{start_number + i}"
                    Bed.objects.get_or_create(
                        ward=ward,
                        bed_number=bed_number,
                        defaults={'is_operational': True, 'is_occupied': False}
                    )
                
                messages.success(request, f"{ward.total_beds} beds generated for {ward.name}")
            
            elif action == 'delete_ward':
                ward_id = request.POST.get('ward_id')
                ward = Ward.objects.get(id=ward_id)
                ward_name = ward.name
                ward.delete()
                messages.success(request, f"Ward '{ward_name}' deleted")
            
            elif action == 'delete_bed':
                bed_id = request.POST.get('bed_id')
                bed = Bed.objects.get(id=bed_id)
                bed_number = bed.bed_number
                bed.delete()
                messages.success(request, f"Bed '{bed_number}' deleted")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect('manage_wards')
    
    # GET - display wards and beds
    wards = Ward.objects.prefetch_related('beds').all()
    
    context = {
        'wards': wards,
        'ward_types': Ward.WARD_TYPE_CHOICES,
    }
    
    return render(request, 'hospital/manage_wards.html', context)

# bed occupancy report for hospital staff
@login_required
def bed_occupancy_reports(request):
    """Main bed occupancy dashboard with multiple views"""
    
    # Check approval and role
    if not request.user.profile.is_approved:
        return redirect('home')
    
    if request.user.profile.role != 'hospital_staff':
        return redirect('home')
    
    # Get filter parameters
    ward_filter = request.GET.get('ward', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Parse dates
    from datetime import datetime, timedelta
    if date_from:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        start_date = timezone.now() - timedelta(days=30)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
        end_date = date_to_obj
    else:
        end_date = timezone.now()
    
    # === CURRENT OCCUPANCY SNAPSHOT ===
    current_stats = []
    total_beds = 0
    total_occupied = 0
    total_available = 0
    total_maintenance = 0
    
    for ward in Ward.objects.all():
        ward_beds = Bed.objects.filter(ward=ward, is_operational=True)
        occupied = ward_beds.filter(is_occupied=True).count()
        available = ward_beds.filter(is_occupied=False).count()
        total = ward_beds.count()
        
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        
        current_stats.append({
            'ward': ward,
            'total_beds': total,
            'occupied': occupied,
            'available': available,
            'occupancy_rate': round(occupancy_rate, 1)
        })
        
        total_beds += total
        total_occupied += occupied
        total_available += available
    
    overall_occupancy_rate = (total_occupied / total_beds * 100) if total_beds > 0 else 0
    
    # === HISTORICAL DATA ===
    # Get all discharged patients in date range
    discharges = PatientAdmission.objects.filter(
        status='discharged',
        actual_discharge_date__range=[start_date, end_date]
    )
    
    if ward_filter:
        discharges = discharges.filter(bed__ward_id=ward_filter)
    
    # Calculate average length of stay
    total_los = 0
    los_count = 0
    
    for discharge in discharges:
        if discharge.admission_date and discharge.actual_discharge_date:
            los = (discharge.actual_discharge_date - discharge.admission_date).total_seconds() / 86400
            total_los += los
            los_count += 1
    
    avg_los_days = round(total_los / los_count, 1) if los_count > 0 else 0
    
    # === BED TURNOVER RATE ===
    total_discharges = discharges.count()
    days_in_period = (end_date - start_date).days or 1
    turnover_rate = (total_discharges / total_beds / days_in_period * 100) if total_beds > 0 else 0
    
    # === CURRENT PATIENTS WITH PREDICTED DISCHARGE ===
    current_patients = PatientAdmission.objects.filter(
        status='admitted'
    ).select_related('bed', 'bed__ward')
    
    if ward_filter:
        current_patients = current_patients.filter(bed__ward_id=ward_filter)
    
    patients_with_predictions = []
    for patient in current_patients:
        if patient.predicted_discharge_date:
            days_remaining = (patient.predicted_discharge_date - date.today()).days
            
            patients_with_predictions.append({
                'patient': patient,
                'expected_discharge': patient.predicted_discharge_date,
                'days_remaining': days_remaining,
                'ward': patient.bed.ward.name if patient.bed else 'N/A',
                'bed': patient.bed.bed_number if patient.bed else 'N/A'
            })
    
    # Sort by expected discharge date
    patients_with_predictions.sort(key=lambda x: x['expected_discharge'])
    
    # === WARD COMPARISON ===
    ward_comparison = []
    for ward in Ward.objects.all():
        ward_discharges = PatientAdmission.objects.filter(
            bed__ward=ward,
            status='discharged',
            actual_discharge_date__range=[start_date, end_date]
        )
        
        ward_total_los = 0
        ward_los_count = 0
        
        for discharge in ward_discharges:
            if discharge.admission_date and discharge.actual_discharge_date:
                los = (discharge.actual_discharge_date - discharge.admission_date).total_seconds() / 86400
                ward_total_los += los
                ward_los_count += 1
        
        ward_avg_los = round(ward_total_los / ward_los_count, 1) if ward_los_count > 0 else 0
        
        ward_comparison.append({
            'ward': ward,
            'total_discharges': ward_discharges.count(),
            'avg_los': ward_avg_los
        })
    
    context = {
        'current_stats': current_stats,
        'overall_occupancy_rate': round(overall_occupancy_rate, 1),
        'total_beds': total_beds,
        'total_occupied': total_occupied,
        'total_available': total_available,
        'avg_los_days': avg_los_days,
        'total_discharges': total_discharges,
        'turnover_rate': round(turnover_rate, 2),
        'patients_with_predictions': patients_with_predictions[:10],
        'ward_comparison': ward_comparison,
        'wards': Ward.objects.all(),
        'ward_filter': ward_filter,
        'date_from': date_from or start_date.strftime('%Y-%m-%d'),
        'date_to': date_to or end_date.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'hospital/bed_occupancy_reports.html', context)


@login_required
def export_occupancy_report(request):
    """Export occupancy data as CSV"""
    import csv
    from django.http import HttpResponse
    
    # Check authorization
    if not request.user.profile.is_approved or request.user.profile.role != 'hospital_staff':
        return redirect('home')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bed_occupancy_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Ward', 'Total Beds', 'Occupied', 'Available', 'Occupancy Rate (%)'])
    
    for ward in Ward.objects.all():
        ward_beds = Bed.objects.filter(ward=ward, is_operational=True)
        total = ward_beds.count()
        occupied = ward_beds.filter(is_occupied=True).count()
        available = ward_beds.filter(is_occupied=False).count()
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        
        writer.writerow([
            ward.name,
            total,
            occupied,
            available,
            f"{occupancy_rate:.1f}"
        ])
    
    return response

# optiona but useful - add view to see bed logs
# @login_required
# def bed_status_logs(request):
#     """View all bed status change logs"""
#     if not request.user.profile.is_approved:
#         return redirect('home')
    
#     # Only IT Support and Hospital Staff can view logs
#     if request.user.profile.role not in ['it_support', 'hospital_staff']:
#         return redirect('home')
    
#     # Get filter parameters
#     bed_filter = request.GET.get('bed', '')
#     date_from = request.GET.get('date_from', '')
#     date_to = request.GET.get('date_to', '')
    
#     # Base query
#     logs = BedStatusLog.objects.select_related('bed', 'bed__ward', 'patient', 'changed_by').all()
    
#     # Apply filters
#     if bed_filter:
#         logs = logs.filter(bed__id=bed_filter)
    
#     if date_from:
#         logs = logs.filter(changed_at__gte=date_from)
    
#     if date_to:
#         from datetime import datetime, timedelta
#         date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
#         logs = logs.filter(changed_at__lt=date_to_obj)
    
#     # Order by most recent
#     logs = logs.order_by('-changed_at')[:100]  # Limit to 100 most recent
    
#     # Get all beds for filter dropdown
#     beds = Bed.objects.select_related('ward').all()
    
#     context = {
#         'logs': logs,
#         'beds': beds,
#         'bed_filter': bed_filter,
#         'date_from': date_from,
#         'date_to': date_to,
#         'total_logs': logs.count(),
#     }
    
#     return render(request, 'hospital/bed_status_logs.html', context)

@login_required
def discharge_alerts(request):
    """Show patients due for discharge soon - helps prepare discharge process"""
    if not request.user.profile.is_approved:
        return redirect('home')
    
    # Nurses and Hospital Staff can view
    if request.user.profile.role not in ['nurse', 'hospital_staff']:
        return redirect('home')
    
    from datetime import date, timedelta
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    # Patients due TODAY (URGENT)
    due_today = PatientAdmission.objects.filter(
        status='admitted',
        predicted_discharge_date=today
    ).select_related('bed', 'bed__ward', 'assigned_by').order_by('bed__ward__name', 'bed__bed_number')
    
    # Patients due TOMORROW
    due_tomorrow = PatientAdmission.objects.filter(
        status='admitted',
        predicted_discharge_date=tomorrow
    ).select_related('bed', 'bed__ward', 'assigned_by').order_by('bed__ward__name', 'bed__bed_number')
    
    # Patients due in 2 DAYS
    due_in_2_days = PatientAdmission.objects.filter(
        status='admitted',
        predicted_discharge_date=day_after_tomorrow
    ).select_related('bed', 'bed__ward', 'assigned_by').order_by('bed__ward__name', 'bed__bed_number')
    
    # OVERDUE patients (predicted discharge date passed but still admitted)
    overdue = PatientAdmission.objects.filter(
        status='admitted',
        predicted_discharge_date__lt=today
    ).select_related('bed', 'bed__ward', 'assigned_by').order_by('predicted_discharge_date')
    
    # Calculate stats
    total_alerts = due_today.count() + due_tomorrow.count() + overdue.count()
    
    # Next 7 days summary
    next_7_days_summary = []
    for i in range(7):
        forecast_date = today + timedelta(days=i)
        count = PatientAdmission.objects.filter(
            status='admitted',
            predicted_discharge_date=forecast_date
        ).count()
        
        next_7_days_summary.append({
            'date': forecast_date,
            'day_name': forecast_date.strftime('%A'),
            'count': count,
            'is_today': (i == 0),
            'is_tomorrow': (i == 1),
        })
    
    context = {
        'due_today': due_today,
        'due_tomorrow': due_tomorrow,
        'due_in_2_days': due_in_2_days,
        'overdue': overdue,
        'total_alerts': total_alerts,
        'next_7_days_summary': next_7_days_summary,
        'today': today,
    }
    
    return render(request, 'hospital/discharge_alerts.html', context)

@login_required
def bed_availability_forecast(request):
    """Show when beds will become available based on predicted discharge dates"""
    if not request.user.profile.is_approved:
        return redirect('home')
    
    # All roles can view this (nurses, hospital staff)
    if request.user.profile.role not in ['nurse', 'hospital_staff']:
        return redirect('home')
    
    from datetime import date, timedelta
    
    # Get all admitted patients with predicted discharge dates
    upcoming_discharges = []
    
    for admission in PatientAdmission.objects.filter(status='admitted').select_related('bed', 'bed__ward'):
        if admission.predicted_discharge_date:
            days_until = (admission.predicted_discharge_date - date.today()).days
            
            upcoming_discharges.append({
                'patient': admission,
                'bed': admission.bed,
                'ward': admission.bed.ward,
                'predicted_discharge': admission.predicted_discharge_date,
                'days_until': days_until,
                'admitted_on': admission.admission_date,
                'predicted_los': admission.predicted_los,
            })
    
    # Sort by discharge date (soonest first)
    upcoming_discharges.sort(key=lambda x: x['predicted_discharge'])
    
    # Group by date
    forecast_by_date = {}
    for discharge in upcoming_discharges:
        discharge_date = discharge['predicted_discharge']
        if discharge_date not in forecast_by_date:
            forecast_by_date[discharge_date] = []
        forecast_by_date[discharge_date].append(discharge)
    
    # Next 7 days forecast
    today = date.today()
    next_7_days = []
    
    for i in range(7):
        forecast_date = today + timedelta(days=i)
        beds_freeing = len(forecast_by_date.get(forecast_date, []))
        
        next_7_days.append({
            'date': forecast_date,
            'day_name': forecast_date.strftime('%A'),
            'beds_freeing': beds_freeing,
            'discharges': forecast_by_date.get(forecast_date, []),
            'is_today': (i == 0),
            'is_tomorrow': (i == 1),
        })
    
    # Calculate total available beds if all predictions are accurate
    current_available = Bed.objects.filter(is_occupied=False, is_operational=True).count()
    total_beds = Bed.objects.filter(is_operational=True).count()
    current_occupied = Bed.objects.filter(is_occupied=True, is_operational=True).count()
    
    # Group by ward
    ward_forecast = {}
    for discharge in upcoming_discharges:
        ward_name = discharge['ward'].name
        if ward_name not in ward_forecast:
            ward_forecast[ward_name] = []
        ward_forecast[ward_name].append(discharge)
    
    context = {
        'upcoming_discharges': upcoming_discharges[:30],  # Show next 30
        'next_7_days': next_7_days,
        'current_available': current_available,
        'current_occupied': current_occupied,
        'total_beds': total_beds,
        'forecast_by_date': forecast_by_date,
        'ward_forecast': ward_forecast,
        'today': today,
    }
    
    return render(request, 'hospital/bed_availability_forecast.html', context)

