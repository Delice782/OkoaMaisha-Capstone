{% comment %} {% extends 'hospital/base.html' %}

{% block title %}Current Patients - OkoaMaisha Hospital{% endblock %}

{% block content %}

<!-- Page Header -->
<div class="page-header">
    <div>
        <h1 class="page-title">Current Patients</h1>
        <p class="page-subtitle">{{ total_patients }} patient(s) currently admitted</p>
    </div>
    <a href="{% url 'dashboard' %}" class="btn">Back to Dashboard</a>
</div>

<!-- Messages -->
{% if messages %}
<div style="margin-bottom: 1.5rem;">
    {% for message in messages %}
    <div class="alert">
        {{ message }}
    </div>
    {% endfor %}
</div>
{% endif %}

<!-- Filters -->
<div class="card section">
    <form method="GET" style="display: flex; gap: 1rem; align-items: end;">
        <div style="flex: 1;">
            <label class="form-label">Search Patient</label>
            <input type="text" name="search" value="{{ search_query }}" placeholder="Search by name or patient ID" class="form-input">
        </div>
        
        <div style="flex: 1;">
            <label class="form-label">Filter by Ward</label>
            <select name="ward" class="form-input">
                <option value="">All Wards</option>
                {% for ward in wards %}
                <option value="{{ ward.id }}" {% if ward_filter == ward.id|stringformat:"s" %}selected{% endif %}>
                    {{ ward.name }}
                </option>
                {% endfor %}
            </select>
        </div>
        
        <button type="submit" class="btn">Filter</button>
        
        <a href="{% url 'view_patients' %}" class="btn">Clear</a>
    </form>
</div>

<!-- Patients Table -->
<div class="card">
    {% if patients %}
    <div class="table-container">
        <table class="table">
            <thead>
                <tr>
                    <th>Patient Name</th>
                    <th>Patient ID</th>
                    <th>Age/Gender</th>
                    <th>Ward</th>
                    <th>Bed</th>
                    <th>Admission Date</th>
                    <th>Predicted LoS</th>
                    <th>Days Here</th>
                    <th>Actions</th>
                    <th>Re-Predict</th>

                </tr>
            </thead>
            <tbody>
                {% for patient in patients %}
                <tr>
                    <td>
                        <span class="patient-name">{{ patient.patient_name }}</span>
                    </td>
                    <td>{{ patient.patient_id }}</td>
                    <td>{{ patient.age|default:"N/A" }} / {{ patient.gender }}</td>
                    <td>{{ patient.bed.ward.name }}</td>
                    <td>
                        <span class="badge">{{ patient.bed.bed_number }}</span>
                    </td>
                    <td>{{ patient.admission_date|date:"M d, Y" }}</td>
                    <td>
                        {% if patient.predicted_los %}
                            {{ patient.predicted_los }} days
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                    <td>{{ patient.admission_date|timesince }}</td>
                    <td>
                        <a href="{% url 'discharge_patient' patient.id %}" class="btn btn-danger" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
                            Discharge
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div style="text-align: center; padding: 3rem 1.5rem;">
        <h2 style="color: var(--text-secondary); font-size: 1.25rem; margin-bottom: 0.5rem;">No patients found</h2>
        <p class="empty-state" style="padding: 0; margin-bottom: 1.5rem;">
            {% if search_query or ward_filter %}
                Try adjusting your filters
            {% else %}
                No patients currently admitted
            {% endif %}
        </p>
        <a href="{% url 'assign_bed' %}" class="btn">Admit New Patient</a>
    </div>
    {% endif %}
</div>

{% endblock %} {% endcomment %}
