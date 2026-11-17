
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Admin Dashboard</h2>
        <p class="text-muted">Examination Management Portal</p>
      </div>
      <button class="btn btn-danger" @click="logout">
        <i class="bi bi-box-arrow-right me-2"></i>Logout
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-2">Loading dashboard...</p>
    </div>

    <template v-else>
      <div class="row g-3">
        <div
          v-for="item in stats"
          :key="item.label"
          class="col-12 col-sm-6 col-lg-3"
        >
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <div class="text-muted mb-2">
                <i :class="item.icon" class="me-2"></i>
                {{ item.label }}
              </div>
              <h2 class="fw-bold mb-0">{{ item.value }}</h2>
            </div>
          </div>
        </div>
      </div>

          <div class="card border-0 shadow-sm mt-4">
      <div class="card-body">
        <h5>Quick Actions</h5>

      <div class="d-flex flex-wrap gap-2 mt-3">
        <router-link to="/admin/courses" class="btn btn-primary">
          <i class="bi bi-book me-2"></i>Manage Courses
        </router-link>

        <router-link to="/admin/examinations" class="btn btn-success">
          <i class="bi bi-journal-text me-2"></i>Manage Examinations
        </router-link>

        <router-link to="/admin/rubrics" class="btn btn-info text-white">
          <i class="bi bi-list-check me-2"></i>Manage Rubrics
        </router-link>

        <router-link to="/admin/examiners" class="btn btn-primary">
          <i class="bi bi-person-badge me-2"></i>Manage Examiners
        </router-link>

        <router-link to="/admin/assignments" class="btn btn-warning">
          <i class="bi bi-person-check me-2"></i>Assign Examiners
        </router-link>

        <router-link to="/admin/results" class="btn btn-success">
          <i class="bi bi-award me-2"></i>Manage Results
        </router-link>
      </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api.js";

const router = useRouter();
const loading = ref(true);
const error = ref("");
const stats = ref([]);

const fields = [
  ["total_courses", "Courses", "bi bi-book"],
  ["total_examinations", "Examinations", "bi bi-journal-text"],
  ["total_students", "Students", "bi bi-people"],
  ["total_examiners", "Examiners", "bi bi-person-badge"],
  ["total_slots", "Examination Slots", "bi bi-calendar"],
  ["active_bookings", "Active Bookings", "bi bi-calendar-check"],
  ["total_evaluations", "Evaluations", "bi bi-clipboard-check"],
  ["published_results", "Published Results", "bi bi-award"],
];

async function loadDashboard() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/admin/dashboard");
    const data = response.data.statistics;

    stats.value = fields.map(([key, label, icon]) => ({
      label,
      icon,
      value: data[key] ?? 0,
    }));
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to load dashboard";
  } finally {
    loading.value = false;
  }
}

async function logout() {
  try {
    await api.post("/auth/logout");
    sessionStorage.removeItem("user");
    await router.push("/login");
  } catch (err) {
    error.value =
      err.response?.data?.message || "Logout failed";
  }
}

onMounted(loadDashboard);
</script>
