function loadDashboard() {
    const role = localStorage.getItem("role");

    document.getElementById("doctorDashboard").style.display = "none";
    document.getElementById("nurseDashboard").style.display = "none";
    document.getElementById("adminDashboard").style.display = "none";

    if (role === "Doctor") {
        document.getElementById("doctorDashboard").style.display = "block";
    } else if (role === "Nurse") {
        document.getElementById("nurseDashboard").style.display = "block";
    } else if (role === "Administrator") {
        document.getElementById("adminDashboard").style.display = "block";
    }
}
