import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from hospital.models import Hospital, Ward, Bed

# Clear existing wards and beds
Ward.objects.all().delete()
print("Cleared existing wards and beds")

# Get hospitals
h1 = Hospital.objects.get(name="Ridge Hospital")
h2 = Hospital.objects.get(name="Police Hospital")
h3 = Hospital.objects.get(name="Korle Bu Teaching Hospital")

# === RIDGE HOSPITAL ===
w1 = Ward.objects.create(hospital=h1, name="ICU", ward_type="icu", total_beds=5, floor=2, gender_restriction="mixed")
w2 = Ward.objects.create(hospital=h1, name="General Ward", ward_type="general", total_beds=10, floor=1, gender_restriction="mixed")

for i in range(5):
    Bed.objects.create(ward=w1, bed_number=f"ICU-{i+1}", is_operational=True, gender_restriction="mixed")

for i in range(5):
    Bed.objects.create(ward=w2, bed_number=f"GEN-M-{i+1}", is_operational=True, gender_restriction="male")

for i in range(5):
    Bed.objects.create(ward=w2, bed_number=f"GEN-F-{i+1}", is_operational=True, gender_restriction="female")

# === POLICE HOSPITAL ===
w3 = Ward.objects.create(hospital=h2, name="ICU", ward_type="icu", total_beds=4, floor=1, gender_restriction="mixed")
w4 = Ward.objects.create(hospital=h2, name="General Ward", ward_type="general", total_beds=8, floor=1, gender_restriction="mixed")

for i in range(4):
    Bed.objects.create(ward=w3, bed_number=f"ICU-{i+1}", is_operational=True, gender_restriction="mixed")

for i in range(4):
    Bed.objects.create(ward=w4, bed_number=f"GEN-M-{i+1}", is_operational=True, gender_restriction="male")

for i in range(4):
    Bed.objects.create(ward=w4, bed_number=f"GEN-F-{i+1}", is_operational=True, gender_restriction="female")

# === KORLE BU ===
w5 = Ward.objects.create(hospital=h3, name="ICU", ward_type="icu", total_beds=10, floor=3, gender_restriction="mixed")
w6 = Ward.objects.create(hospital=h3, name="General Ward", ward_type="general", total_beds=20, floor=1, gender_restriction="mixed")
w7 = Ward.objects.create(hospital=h3, name="Maternity", ward_type="maternity", total_beds=15, floor=2, gender_restriction="female")

for i in range(10):
    Bed.objects.create(ward=w5, bed_number=f"ICU-{i+1}", is_operational=True, gender_restriction="mixed")

for i in range(10):
    Bed.objects.create(ward=w6, bed_number=f"GEN-M-{i+1}", is_operational=True, gender_restriction="male")

for i in range(10):
    Bed.objects.create(ward=w6, bed_number=f"GEN-F-{i+1}", is_operational=True, gender_restriction="female")

for i in range(15):
    Bed.objects.create(ward=w7, bed_number=f"MAT-{i+1}", is_operational=True, gender_restriction="female")

print("✅ Done!")
print(f"Ridge Hospital: {Bed.objects.filter(ward__hospital=h1).count()} beds")
print(f"Police Hospital: {Bed.objects.filter(ward__hospital=h2).count()} beds")
print(f"Korle Bu: {Bed.objects.filter(ward__hospital=h3).count()} beds")