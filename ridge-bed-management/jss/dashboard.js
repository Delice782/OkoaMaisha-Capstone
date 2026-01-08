// ===================== INITIALIZATION & DATA STRUCTURE =====================

// Initialize data structure if not exists
function initializeData() {
    if (!localStorage.getItem('beds')) {
        localStorage.setItem('beds', JSON.stringify({}));
    }
    if (!localStorage.getItem('patients')) {
        localStorage.setItem('patients', JSON.stringify({}));
    }
    if (!localStorage.getItem('signupData')) {
        // Add default users
        const defaultUsers = {
            'admin@hospital.com': {
                firstName: 'Admin',
                lastName: 'User',
                role: 'admin',
                password: btoa('admin123'),
                department: 'Administration',
                status: 'active'
            },
            'nurse@hospital.com': {
                firstName: 'Nurse',
                lastName: 'Smith',
                role: 'nurse',
                password: btoa('nurse123'),
                department: 'General Ward',
                status: 'active'
            },
            'doctor@hospital.com': {
                firstName: 'Dr. John',
                lastName: 'Doe',
                role: 'doctor',
                password: btoa('doctor123'),
                department: 'General Ward',
                status: 'active'
            },
            'medadmin@hospital.com': {
                firstName: 'Medical',
                lastName: 'Admin',
                role: 'medicalAdmin',
                password: btoa('medadmin123'),
                department: 'Administration',
                status: 'active'
            }
        };
        localStorage.setItem('signupData', JSON.stringify(defaultUsers));
    }
}

// Utility functions
function saveData(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function loadData(key) {
    return JSON.parse(localStorage.getItem(key) || '{}');
}

function generateID(prefix) {
    return prefix + '-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function calculateDaysBetween(date1, date2) {
    const diffTime = Math.abs(new Date(date2) - new Date(date1));
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// ===================== PREDICTIVE ANALYTICS MODULE =====================

// Simple predictive model based on diagnosis and age
function predictLengthOfStay(diagnosis, age, department) {
    const baseDays = {
        'pneumonia': 7,
        'covid': 10,
        'surgery': 5,
        'fracture': 14,
        'heart': 8,
        'stroke': 12,
        'infection': 6,
        'diabetes': 4,
        'hypertension': 3,
        'asthma': 4,
        'default': 5
    };
    
    // Find matching diagnosis
    let days = baseDays.default;
    const diagnosisLower = diagnosis.toLowerCase();
    
    for (let key in baseDays) {
        if (diagnosisLower.includes(key)) {
            days = baseDays[key];
            break;
        }
    }
    
    // Age factor
    if (age > 65) days += 2;
    if (age < 18) days += 1;
    
    // Department factor
    if (department === 'ICU') days += 3;
    if (department === 'Emergency') days -= 1;
    
    // Add random variation (-1 to +2 days)
    days += Math.floor(Math.random() * 4) - 1;
    
    return Math.max(1, days);
}

function calculateDischargeDate(admissionDate, lengthOfStay) {
    const admission = new Date(admissionDate);
    const discharge = new Date(admission);
    discharge.setDate(discharge.getDate() + lengthOfStay);
    return discharge.toISOString().split('T')[0];
}

function getPredictedDischarges(days = 7) {
    const patients = loadData('patients');
    const predictions = [];
    const today = new Date();
    
    for (let id in patients) {
        const patient = patients[id];
        if (patient.status === 'admitted' && patient.predictedDischarge) {
            const dischargeDate = new Date(patient.predictedDischarge);
            const daysUntil = calculateDaysBetween(today, dischargeDate);
            
            if (daysUntil <= days && dischargeDate >= today) {
                predictions.push({
                    ...patient,
                    id: id,
                    daysUntil: daysUntil
                });
            }
        }
    }
    
    return predictions.sort((a, b) => a.daysUntil - b.daysUntil);
}

// ===================== BED MANAGEMENT MODULE =====================

function getAvailableBed(department) {
    const beds = loadData('beds');
    
    for (let bedId in beds) {
        const bed = beds[bedId];
        if (bed.status === 'available' && bed.department === department) {
            return bedId;
        }
    }
    
    return null;
}

function assignBedToPatient(bedId, patientId) {
    const beds = loadData('beds');
    const patients = loadData('patients');
    
    if (beds[bedId] && patients[patientId]) {
        beds[bedId].status = 'occupied';
        beds[bedId].patientId = patientId;
        beds[bedId].lastUpdated = new Date().toISOString();
        
        patients[patientId].bedNumber = bedId;
        patients[patientId].status = 'admitted';
        
        saveData('beds', beds);
        saveData('patients', patients);
        
        return true;
    }
    
    return false;
}

function releaseBed(bedId) {
    const beds = loadData('beds');
    
    if (beds[bedId]) {
        const patientId = beds[bedId].patientId;
        
        beds[bedId].status = 'cleaning';
        delete beds[bedId].patientId;
        beds[bedId].lastUpdated = new Date().toISOString();
        
        saveData('beds', beds);
        
        // Update patient status
        if (patientId) {
            const patients = loadData('patients');
            if (patients[patientId]) {
                patients[patientId].status = 'discharged';
                patients[patientId].dischargeDate = new Date().toISOString().split('T')[0];
                saveData('patients', patients);
            }
        }
        
        return true;
    }
    
    return false;
}

function updateBedStatus(bedId, newStatus) {
    const beds = loadData('beds');
    
    if (beds[bedId]) {
        beds[bedId].status = newStatus;
        beds[bedId].lastUpdated = new Date().toISOString();
        saveData('beds', beds);
        return true;
    }
    
    return false;
}

function getBedStatistics() {
    const beds = loadData('beds');
    const stats = {
        total: 0,
        available: 0,
        occupied: 0,
        reserved: 0,
        cleaning: 0,
        byDepartment: {}
    };
    
    for (let bedId in beds) {
        const bed = beds[bedId];
        stats.total++;
        stats[bed.status] = (stats[bed.status] || 0) + 1;
        
        if (!stats.byDepartment[bed.department]) {
            stats.byDepartment[bed.department] = {
                total: 0,
                available: 0,
                occupied: 0
            };
        }
        
        stats.byDepartment[bed.department].total++;
        if (bed.status === 'available') {
            stats.byDepartment[bed.department].available++;
        } else if (bed.status === 'occupied') {
            stats.byDepartment[bed.department].occupied++;
        }
    }
    
    return stats;
}

// ===================== PATIENT MANAGEMENT MODULE =====================

function admitPatient(patientData) {
    const patientId = generateID('PAT');
    const patients = loadData('patients');
    
    // Predict length of stay
    const lengthOfStay = predictLengthOfStay(
        patientData.diagnosis,
        patientData.age,
        patientData.department
    );
    
    // Calculate predicted discharge date
    const predictedDischarge = calculateDischargeDate(
        patientData.admissionDate,
        lengthOfStay
    );
    
    // Find available bed
    const bedId = getAvailableBed(patientData.department);
    
    if (!bedId) {
        return { success: false, message: 'No available beds in ' + patientData.department };
    }
    
    // Create patient record
    patients[patientId] = {
        ...patientData,
        patientId: patientId,
        bedNumber: bedId,
        status: 'admitted',
        predictedLengthOfStay: lengthOfStay,
        predictedDischarge: predictedDischarge,
        admittedBy: localStorage.getItem('userEmail') || 'system',
        admittedAt: new Date().toISOString()
    };
    
    saveData('patients', patients);
    
    // Assign bed
    assignBedToPatient(bedId, patientId);
    
    return {
        success: true,
        patientId: patientId,
        bedId: bedId,
        predictedDischarge: predictedDischarge,
        lengthOfStay: lengthOfStay
    };
}

function dischargePatient(patientId) {
    const patients = loadData('patients');
    const patient = patients[patientId];
    
    if (patient && patient.bedNumber) {
        releaseBed(patient.bedNumber);
        patient.status = 'discharged';
        patient.actualDischargeDate = new Date().toISOString().split('T')[0];
        patient.dischargedBy = localStorage.getItem('userEmail') || 'system';
        
        saveData('patients', patients);
        return true;
    }
    
    return false;
}

function transferPatient(patientId, newDepartment) {
    const patients = loadData('patients');
    const patient = patients[patientId];
    
    if (patient) {
        // Release current bed
        if (patient.bedNumber) {
            releaseBed(patient.bedNumber);
        }
        
        // Find new bed
        const newBedId = getAvailableBed(newDepartment);
        
        if (!newBedId) {
            return { success: false, message: 'No available beds in ' + newDepartment };
        }
        
        // Update patient
        patient.department = newDepartment;
        patient.bedNumber = newBedId;
        patient.transferHistory = patient.transferHistory || [];
        patient.transferHistory.push({
            date: new Date().toISOString(),
            department: newDepartment,
            bed: newBedId
        });
        
        saveData('patients', patients);
        assignBedToPatient(newBedId, patientId);
        
        return { success: true, newBedId: newBedId };
    }
    
    return { success: false, message: 'Patient not found' };
}

// ===================== DASHBOARD LOADING =====================

function loadDashboard() {
    initializeData();
    
    const role = localStorage.getItem('userRole');
    
    if (!role) {
        alert('Unauthorized access.');
        window.location.href = 'login.html';
        return;
    }
    
    showDashboard(role);
    updateUserInfo();
}

function showDashboard(role) {
    document.querySelectorAll('.role-section').forEach(section => {
        section.classList.remove('active');
    });
    
    const dashboardMap = {
        'admin': 'adminDashboard',
        'medicalAdmin': 'medicalAdminDashboard',
        'nurse': 'nurseDashboard',
        'doctor': 'doctorDashboard'
    };
    
    const targetId = dashboardMap[role];
    const target = document.getElementById(targetId);
    
    if (!target) {
        alert('Invalid role.');
        window.location.href = 'login.html';
        return;
    }
    
    target.classList.add('active');
    
    // Load role-specific data
    switch(role) {
        case 'admin':
            loadAdminDashboard();
            break;
        case 'medicalAdmin':
            loadMedicalAdminDashboard();
            break;
        case 'nurse':
            loadNurseDashboard();
            break;
        case 'doctor':
            loadDoctorDashboard();
            break;
    }
}

function updateUserInfo() {
    const firstName = localStorage.getItem('firstName') || '';
    const lastName = localStorage.getItem('lastName') || '';
    const role = localStorage.getItem('userRole') || '';
    
    const roleNames = {
        'admin': 'Hospital Administrator',
        'medicalAdmin': 'Medical Administrative Staff',
        'nurse': 'Nurse',
        'doctor': 'Doctor'
    };
    
    const fullName = `${firstName} ${lastName}`.trim();
    const roleLabel = roleNames[role] || role;
    
    document.getElementById('userName').textContent = fullName || 'User';
    document.getElementById('userRole').textContent = roleLabel;
    document.getElementById('userAvatar').textContent = 
        (firstName[0] || 'U') + (lastName[0] || '');
}

// ===================== ADMIN DASHBOARD =====================

function loadAdminDashboard() {
    const users = loadData('signupData');
    const stats = getBedStatistics();
    const patients = loadData('patients');
    
    // Count active patients
    let activePatients = 0;
    for (let id in patients) {
        if (patients[id].status === 'admitted') activePatients++;
    }
    
    // Update stats
    document.getElementById('adminTotalUsers').textContent = Object.keys(users).length;
    document.getElementById('adminTotalBeds').textContent = stats.total;
    document.getElementById('adminTotalPatients').textContent = activePatients;
    
    const occupancyRate = stats.total > 0 ? 
        Math.round((stats.occupied / stats.total) * 100) : 0;
    document.getElementById('adminOccupancyRate').textContent = occupancyRate + '%';
    
    // Update department stats
    const deptStats = stats.byDepartment;
    
    if (deptStats['Emergency']) {
        document.getElementById('emergencyBeds').textContent = 
            `${deptStats['Emergency'].available}/${deptStats['Emergency'].total}`;
    }
    if (deptStats['ICU']) {
        document.getElementById('icuBeds').textContent = 
            `${deptStats['ICU'].available}/${deptStats['ICU'].total}`;
    }
    if (deptStats['General Ward']) {
        document.getElementById('generalBeds').textContent = 
            `${deptStats['General Ward'].available}/${deptStats['General Ward'].total}`;
    }
    if (deptStats['Pediatrics']) {
        document.getElementById('pediatricsBeds').textContent = 
            `${deptStats['Pediatrics'].available}/${deptStats['Pediatrics'].total}`;
    }
    
    // Load user table
    renderAdminUserTable();
    
    // Load performance chart
    renderAdminPerformanceChart();
}

function renderAdminUserTable() {
    const users = loadData('signupData');
    const tbody = document.querySelector('#adminUserTable tbody');
    tbody.innerHTML = '';
    
    const roleNames = {
        'admin': 'Administrator',
        'medicalAdmin': 'Medical Admin',
        'nurse': 'Nurse',
        'doctor': 'Doctor'
    };
    
    for (let email in users) {
        const user = users[email];
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${user.firstName} ${user.lastName}</td>
            <td>${email}</td>
            <td>${roleNames[user.role] || user.role}</td>
            <td><span class="status-badge status-available">${user.status || 'active'}</span></td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="editUser('${email}')">Edit</button>
                <button class="btn btn-danger btn-sm" onclick="deactivateUser('${email}')">Deactivate</button>
            </td>
        `;
        tbody.appendChild(tr);
    }
}

function renderAdminPerformanceChart() {
    const ctx = document.getElementById('adminPerformanceChart');
    if (!ctx) return;
    
    const stats = getBedStatistics();
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Available', 'Occupied', 'Reserved', 'Cleaning'],
            datasets: [{
                data: [
                    stats.available || 0,
                    stats.occupied || 0,
                    stats.reserved || 0,
                    stats.cleaning || 0
                ],
                backgroundColor: [
                    '#4caf50',
                    '#f44336',
                    '#ff9800',
                    '#2196f3'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Current Bed Distribution'
                }
            }
        }
    });
}

// ===================== MEDICAL ADMIN DASHBOARD =====================

function loadMedicalAdminDashboard() {
    const patients = loadData('patients');
    const stats = getBedStatistics();
    
    // Count today's admissions
    const today = new Date().toISOString().split('T')[0];
    let todayAdmissions = 0;
    let activePatients = 0;
    
    for (let id in patients) {
        const patient = patients[id];
        if (patient.admissionDate === today) todayAdmissions++;
        if (patient.status === 'admitted') activePatients++;
    }
    
    // Get pending discharges
    const pendingDischarges = getPredictedDischarges(1).length;
    
    // Update stats
    document.getElementById('todayAdmissions').textContent = todayAdmissions;
    document.getElementById('medAdminAvailableBeds').textContent = stats.available || 0;
    document.getElementById('pendingDischarges').textContent = pendingDischarges;
    document.getElementById('medAdminTotalPatients').textContent = activePatients;
    
    // Set today's date as default
    document.getElementById('admissionDate').valueAsDate = new Date();
    
    // Load patient table
    renderMedAdminPatientTable();
}

function renderMedAdminPatientTable() {
    const patients = loadData('patients');
    const tbody = document.querySelector('#medAdminPatientTable tbody');
    tbody.innerHTML = '';
    
    for (let id in patients) {
        const patient = patients[id];
        if (patient.status === 'admitted') {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${patient.patientId}</td>
                <td>${patient.name}</td>
                <td>${patient.age}</td>
                <td>${patient.department}</td>
                <td>${patient.bedNumber || 'N/A'}</td>
                <td>${formatDate(patient.admissionDate)}</td>
                <td>${formatDate(patient.predictedDischarge)}</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="viewPatientDetails('${id}')">View</button>
                    <button class="btn btn-danger btn-sm" onclick="dischargePatientConfirm('${id}')">Discharge</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    }
}

// ===================== NURSE DASHBOARD =====================

function loadNurseDashboard() {
    const stats = getBedStatistics();
    
    // Update bed counts
    document.getElementById('nurseAvailableBeds').textContent = stats.available || 0;
    document.getElementById('nurseOccupiedBeds').textContent = stats.occupied || 0;
    document.getElementById('nurseReservedBeds').textContent = stats.reserved || 0;
    document.getElementById('nurseCleaningBeds').textContent = stats.cleaning || 0;
    
    // Render bed grid and table
    renderBedGrid();
    renderNurseBedTable();
    renderNurseDischargeTable();
}

function renderBedGrid(filter = 'all') {
    const beds = loadData('beds');
    const patients = loadData('patients');
    const container = document.getElementById('bedGridView');
    container.innerHTML = '';
    
    for (let bedId in beds) {
        const bed = beds[bedId];
        
        if (filter !== 'all' && bed.status !== filter) continue;
        
        const bedDiv = document.createElement('div');
        bedDiv.className = `bed-item ${bed.status}`;
        bedDiv.onclick = () => viewBedDetails(bedId);
        
        let patientName = '';
        if (bed.patientId && patients[bed.patientId]) {
            patientName = patients[bed.patientId].name;
        }
        
        bedDiv.innerHTML = `
            <div class="bed-number">${bedId}</div>
            <div class="bed-status">${bed.status}</div>
            ${patientName ? `<div style="font-size:0.75rem;margin-top:0.5rem;">${patientName}</div>` : ''}
        `;
        
        container.appendChild(bedDiv);
    }
}

function filterBeds(status) {
    renderBedGrid(status);
}

function renderNurseBedTable() {
    const beds = loadData('beds');
    const patients = loadData('patients');
    const tbody = document.querySelector('#nurseBedTable tbody');
    tbody.innerHTML = '';
    
    for (let bedId in beds) {
        const bed = beds[bedId];
        
        let patientName = 'N/A';
        if (bed.patientId && patients[bed.patientId]) {
            patientName = patients[bed.patientId].name;
        }
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${bedId}</td>
            <td>${bed.department}</td>
            <td><span class="status-badge status-${bed.status}">${bed.status}</span></td>
            <td>${patientName}</td>
            <td>${bed.lastUpdated ? formatDate(bed.lastUpdated) : 'N/A'}</td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="changeBedStatus('${bedId}')">Change Status</button>
                <button class="btn btn-danger btn-sm" onclick="deleteBed('${bedId}')">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    }
}

function renderNurseDischargeTable() {
    const predictions = getPredictedDischarges(7);
    const tbody = document.querySelector('#nurseDischargeTable tbody');
    tbody.innerHTML = '';
    
    predictions.forEach(patient => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${patient.name}</td>
            <td>${patient.bedNumber}</td>
            <td>${formatDate(patient.admissionDate)}</td>
            <td>${formatDate(patient.predictedDischarge)} (${patient.daysUntil} days)</td>
            <td>
                <button class="btn btn-success btn-sm" onclick="prepareDischarge('${patient.id}')">Prepare Discharge</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// ===================== DOCTOR DASHBOARD =====================

function loadDoctorDashboard() {
    const patients = loadData('patients');
    
    let myPatients = 0;
    let criticalCases = 0;
    let dischargeToday = 0;
    let newAdmissions = 0;
    
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    
    for (let id in patients) {
        const patient = patients[id];
        if (patient.status === 'admitted') {
            myPatients++;
            
            // Count critical (ICU patients)
            if (patient.department === 'ICU') criticalCases++;
            
            // Count discharges today
            if (patient.predictedDischarge === today) dischargeToday++;
            
            // Count new admissions (last 24 hours)
            if (patient.admissionDate >= yesterday) newAdmissions++;
        }
    }
    
    // Update stats
    document.getElementById('doctorPatientCount').textContent = myPatients;
    document.getElementById('criticalCases').textContent = criticalCases;
    document.getElementById('doctorDischargeToday').textContent = dischargeToday;
    document.getElementById('doctorNewAdmissions').textContent = newAdmissions;
    
    // Load tables and charts
    renderDoctorPatientTable();
    renderDoctorPredictions();
    renderDoctorLengthOfStayChart();
    populateDoctorPatientSelect();
}

function renderDoctorPatientTable() {
    const patients = loadData('patients');
    const tbody = document.querySelector('#doctorPatientTable tbody');
    tbody.innerHTML = '';
    
    for (let id in patients) {
        const patient = patients[id];
        if (patient.status === 'admitted') {
            const lengthOfStay = calculateDaysBetween(
                patient.admissionDate,
                new Date().toISOString().split('T')[0]
            );
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${patient.patientId}</td>
                <td>${patient.name}</td>
                <td>${patient.age}/${patient.gender}</td>
                <td>${patient.bedNumber}</td>
                <td>${patient.diagnosis}</td>
                <td>${formatDate(patient.admissionDate)}</td>
                <td>${lengthOfStay} days</td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="viewPatientDetails('${id}')">Details</button>
                    <button class="btn btn-success btn-sm" onclick="planDischarge('${id}')">Plan Discharge</button>
                </td>
            `;
            tbody.appendChild(tr);
        }
    }
}

function renderDoctorPredictions() {
    const predictions = getPredictedDischarges(7);
    const container = document.getElementById('doctorPredictions');
    container.innerHTML = '';
    
    if (predictions.length === 0) {
        container.innerHTML = '<div class="prediction-item">No discharges predicted in the next 7 days</div>';
        return;
    }
    
    predictions.forEach(patient => {
        const div = document.createElement('div');
        div.className = 'prediction-item';
        div.innerHTML = `
            <strong>${patient.name}</strong> - Bed ${patient.bedNumber}<br>
            Expected discharge: ${formatDate(patient.predictedDischarge)} (${patient.daysUntil} days)<br>
            Diagnosis: ${patient.diagnosis}
        `;
        container.appendChild(div);
    });
}

function renderDoctorLengthOfStayChart() {
    const ctx = document.getElementById('doctorLengthOfStayChart');
    if (!ctx) return;
    
    const patients = loadData('patients');
    const stayData = {};
    
    for (let id in patients) {
        const patient = patients[id];
        if (patient.status === 'admitted') {
            const lengthOfStay = calculateDaysBetween(
                patient.admissionDate,
                new Date().toISOString().split('T')[0]
            );
            
            const range = lengthOfStay <= 3 ? '0-3' :
                         lengthOfStay <= 7 ? '4-7' :
                         lengthOfStay <= 14 ? '8-14' : '15+';
            
            stayData[range] = (stayData[range] || 0) + 1;
        }
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-3 days', '4-7 days', '8-14 days', '15+ days'],
            datasets: [{
                label: 'Number of Patients',
                data: [
                    stayData['0-3'] || 0,
                    stayData['4-7'] || 0,
                    stayData['8-14'] || 0,
                    stayData['15+'] || 0
                ],
                backgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Length of Stay Distribution'
                }
            }
        }
    });
}

function populateDoctorPatientSelect() {
    const patients = loadData('patients');
    const select = document.getElementById('doctorSelectPatient');
    select.innerHTML = '<option value="">Choose a patient...</option>';
    
    for (let id in patients) {
        const patient = patients[id];
        if (patient.status === 'admitted') {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = `${patient.name} - Bed ${patient.bedNumber}`;
            select.appendChild(option);
        }
    }
}

// ===================== FORM HANDLERS =====================

// Admission Form
document.getElementById('admissionForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const patientData = {
        name: document.getElementById('patientName').value,
        age: parseInt(document.getElementById('patientAge').value),
        gender: document.getElementById('patientGender').value,
        department: document.getElementById('patientDepartment').value,
        diagnosis: document.getElementById('patientDiagnosis').value,
        contact: document.getElementById('patientContact').value,
        emergencyContact: document.getElementById('emergencyContact').value,
        admissionDate: document.getElementById('admissionDate').value,
        medicalNotes: document.getElementById('medicalNotes').value
    };
    
    const result = admitPatient(patientData);
    
    if (result.success) {
        alert(`Patient admitted successfully!\n\nPatient ID: ${result.patientId}\nBed Number: ${result.bedId}\nPredicted Discharge: ${formatDate(result.predictedDischarge)}\nExpected Stay: ${result.lengthOfStay} days`);
        this.reset();
        loadMedicalAdminDashboard();
    } else {
        alert('Error: ' + result.message);
    }
});

// Add User Form
document.getElementById('addUserForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('userEmail').value.toLowerCase();
    const users = loadData('signupData');
    
    users[email] = {
        firstName: document.getElementById('userFirstName').value,
        lastName: document.getElementById('userLastName').value,
        role: document.getElementById('userRole').value,
        department: document.getElementById('userDepartment').value,
        password: btoa('password123'),
        status: 'active'
    };
    
    saveData('signupData', users);
    closeAddUserModal();
    alert('User created successfully! Default password: password123');
    loadAdminDashboard();
});

// Add Bed Form
document.getElementById('addBedForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const bedId = document.getElementById('bedNumber').value.toUpperCase();
    const beds = loadData('beds');
    
    if (beds[bedId]) {
        alert('Bed number already exists!');
        return;
    }
    
    beds[bedId] = {
        bedNumber: bedId,
        department: document.getElementById('bedDepartment').value,
        status: document.getElementById('bedStatus').value,
        lastUpdated: new Date().toISOString()
    };
    
    saveData('beds', beds);
    closeAddBedModal();
    alert('Bed added successfully!');
    loadNurseDashboard();
});

// ===================== MODAL FUNCTIONS =====================

function openAddUserModal() {
    document.getElementById('addUserModal').classList.add('active');
}

function closeAddUserModal() {
    document.getElementById('addUserModal').classList.remove('active');
    document.getElementById('addUserForm').reset();
}

function openAddBedModal() {
    document.getElementById('addBedModal').classList.add('active');
}

function closeAddBedModal() {
    document.getElementById('addBedModal').classList.remove('active');
    document.getElementById('addBedForm').reset();
}

function closePatientDetailsModal() {
    document.getElementById('patientDetailsModal').classList.remove('active');
}

// ===================== ACTION FUNCTIONS =====================

function viewPatientDetails(patientId) {
    const patients = loadData('patients');
    const patient = patients[patientId];
    
    if (!patient) {
        alert('Patient not found');
        return;
    }
    
    const lengthOfStay = calculateDaysBetween(
        patient.admissionDate,
        new Date().toISOString().split('T')[0]
    );
    
    const content = `
        <div style="padding:1rem;">
            <h4>Patient Information</h4>
            <p><strong>Patient ID:</strong> ${patient.patientId}</p>
            <p><strong>Name:</strong> ${patient.name}</p>
            <p><strong>Age:</strong> ${patient.age}</p>
            <p><strong>Gender:</strong> ${patient.gender}</p>
            <p><strong>Department:</strong> ${patient.department}</p>
            <p><strong>Bed Number:</strong> ${patient.bedNumber}</p>
            
            <h4 style="margin-top:1.5rem;">Medical Information</h4>
            <p><strong>Diagnosis:</strong> ${patient.diagnosis}</p>
            <p><strong>Medical Notes:</strong> ${patient.medicalNotes || 'None'}</p>
            
            <h4 style="margin-top:1.5rem;">Admission Details</h4>
            <p><strong>Admission Date:</strong> ${formatDate(patient.admissionDate)}</p>
            <p><strong>Length of Stay:</strong> ${lengthOfStay} days</p>
            <p><strong>Predicted Discharge:</strong> ${formatDate(patient.predictedDischarge)}</p>
            <p><strong>Status:</strong> ${patient.status}</p>
            
            <h4 style="margin-top:1.5rem;">Contact Information</h4>
            <p><strong>Contact:</strong> ${patient.contact || 'N/A'}</p>
            <p><strong>Emergency Contact:</strong> ${patient.emergencyContact || 'N/A'}</p>
        </div>
    `;
    
    document.getElementById('patientDetailsContent').innerHTML = content;
    document.getElementById('patientDetailsModal').classList.add('active');
}

function dischargePatientConfirm(patientId) {
    if (confirm('Are you sure you want to discharge this patient?')) {
        if (dischargePatient(patientId)) {
            alert('Patient discharged successfully!');
            location.reload();
        } else {
            alert('Error discharging patient');
        }
    }
}

function changeBedStatus(bedId) {
    const newStatus = prompt('Enter new status (available/occupied/reserved/cleaning):');
    
    if (newStatus && ['available', 'occupied', 'reserved', 'cleaning'].includes(newStatus)) {
        if (updateBedStatus(bedId, newStatus)) {
            alert('Bed status updated!');
            loadNurseDashboard();
        }
    } else {
        alert('Invalid status');
    }
}

function deleteBed(bedId) {
    if (confirm('Are you sure you want to delete this bed?')) {
        const beds = loadData('beds');
        delete beds[bedId];
        saveData('beds', beds);
        alert('Bed deleted!');
        loadNurseDashboard();
    }
}

function prepareDischarge(patientId) {
    const patients = loadData('patients');
    const patient = patients[patientId];
    
    if (confirm(`Prepare ${patient.name} for discharge?`)) {
        // Change bed status to cleaning
        if (patient.bedNumber) {
            updateBedStatus(patient.bedNumber, 'cleaning');
        }
        alert('Bed prepared for discharge. Patient can be discharged by medical staff.');
        loadNurseDashboard();
    }
}

function planDischarge(patientId) {
    const patients = loadData('patients');
    const patient = patients[patientId];
    
    const notes = prompt(`Plan discharge for ${patient.name}.\nEnter discharge notes:`);
    
    if (notes) {
        patient.dischargeNotes = notes;
        patient.dischargePlanned = true;
        saveData('patients', patients);
        alert('Discharge planned and notes saved!');
    }
}

function editUser(email) {
    const users = loadData('signupData');
    const user = users[email];
    
    document.getElementById('userFirstName').value = user.firstName;
    document.getElementById('userLastName').value = user.lastName;
    document.getElementById('userEmail').value = email;
    document.getElementById('userRole').value = user.role;
    document.getElementById('userDepartment').value = user.department || '';
    
    openAddUserModal();
}

function deactivateUser(email) {
    if (confirm('Deactivate this user?')) {
        const users = loadData('signupData');
        users[email].status = 'inactive';
        saveData('signupData', users);
        alert('User deactivated!');
        loadAdminDashboard();
    }
}

function updatePatientInfo() {
    const patientId = document.getElementById('doctorSelectPatient').value;
    
    if (!patientId) {
        alert('Please select a patient');
        return;
    }
    
    const patients = loadData('patients');
    const patient = patients[patientId];
    
    patient.treatmentPlan = document.getElementById('treatmentPlan').value;
    patient.vitalsUpdate = document.getElementById('vitalsUpdate').value;
    patient.clinicalNotes = document.getElementById('clinicalNotes').value;
    patient.lastUpdated = new Date().toISOString();
    patient.updatedBy = localStorage.getItem('userEmail');
    
    saveData('patients', patients);
    alert('Patient information updated successfully!');
    
    // Clear form
    document.getElementById('treatmentPlan').value = '';
    document.getElementById('vitalsUpdate').value = '';
    document.getElementById('clinicalNotes').value = '';
    document.getElementById('patientUpdateForm').style.display = 'none';
}

// Show patient update form when patient selected
document.getElementById('doctorSelectPatient')?.addEventListener('change', function() {
    const form = document.getElementById('patientUpdateForm');
    if (this.value) {
        form.style.display = 'block';
        
        // Load existing data
        const patients = loadData('patients');
        const patient = patients[this.value];
        
        if (patient) {
            document.getElementById('treatmentPlan').value = patient.treatmentPlan || '';
            document.getElementById('vitalsUpdate').value = patient.vitalsUpdate || '';
            document.getElementById('clinicalNotes').value = patient.clinicalNotes || '';
        }
    } else {
        form.style.display = 'none';
    }
});

// ===================== NAVIGATION =====================

function showAdmission() {
    const role = localStorage.getItem('userRole');
    if (role === 'medicalAdmin') {
        document.querySelector('nav a.active')?.classList.remove('active');
        document.querySelectorAll('nav a')[1].classList.add('active');
    } else {
        alert('Only Medical Administrative Staff can access admissions');
    }
}

function showPatients() {
    alert('Patient list view - Feature in development');
}

function showReports() {
    alert('Reports view - Feature in development');
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        window.location.href = 'login.html';
    }
}

// ===================== INITIALIZATION =====================

window.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    
    // Add some sample data if database is empty
    const beds = loadData('beds');
    if (Object.keys(beds).length === 0) {
        initializeSampleData();
        location.reload();
    }
});

// Initialize sample data
function initializeSampleData() {
    const sampleBeds = {
        'A-101': { bedNumber: 'A-101', department: 'General Ward', status: 'available', lastUpdated: new Date().toISOString() },
        'A-102': { bedNumber: 'A-102', department: 'General Ward', status: 'available', lastUpdated: new Date().toISOString() },
        'B-201': { bedNumber: 'B-201', department: 'ICU', status: 'available', lastUpdated: new Date().toISOString() },
        'B-202': { bedNumber: 'B-202', department: 'ICU', status: 'available', lastUpdated: new Date().toISOString() },
        'C-301': { bedNumber: 'C-301', department: 'Emergency', status: 'available', lastUpdated: new Date().toISOString() },
        'C-302': { bedNumber: 'C-302', department: 'Emergency', status: 'available', lastUpdated: new Date().toISOString() },
        'D-401': { bedNumber: 'D-401', department: 'Pediatrics', status: 'available', lastUpdated: new Date().toISOString() },
        'D-402': { bedNumber: 'D-402', department: 'Pediatrics', status: 'available', lastUpdated: new Date().toISOString() },
    };
    
    saveData('beds', sampleBeds);
    alert('Sample bed data initialized!');
}