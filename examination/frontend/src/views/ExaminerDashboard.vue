
<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Examiner Dashboard</h2>
        <p class="text-muted mb-0">
          Welcome, {{ examiner.name || "Examiner" }}
        </p>
      </div>

      <button
        class="btn btn-outline-danger"
        :disabled="loggingOut"
        @click="logout"
      >
        <i class="bi bi-box-arrow-right me-2"></i>
        Logout
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Examiner Navigation -->
    <div class="row g-3 mb-4">
    <div class="col-md-6">
        <router-link
        to="/examiner/slots"
        class="btn btn-primary w-100 py-3"
        >
        <i class="bi bi-calendar-event me-2"></i>
        Manage Examination Slots
        </router-link>
    </div>

    <div class="col-md-6">
        <router-link
        to="/examiner/evaluations"
        class="btn btn-success w-100 py-3"
        >
        <i class="bi bi-clipboard-check me-2"></i>
        Evaluate Students
        </router-link>
    </div>
    </div>


    <!-- Profile -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <h5 class="fw-bold mb-3">My Profile</h5>
        <p class="mb-1">
          <strong>Name:</strong> {{ examiner.name || "—" }}
        </p>
        <p class="mb-0">
          <strong>Email:</strong> {{ examiner.email || "—" }}
        </p>
      </div>
    </div>

    <!-- Statistics -->
    <div class="row g-3 mb-4">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-primary-subtle text-primary">
              <i class="bi bi-journal-check fs-4"></i>
            </div>
            <div>
              <p class="text-muted mb-1">Assigned Examinations</p>
              <h3 class="fw-bold mb-0">
                {{ dashboard.assigned_examinations ?? 0 }}
              </h3>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-success-subtle text-success">
              <i class="bi bi-calendar-event fs-4"></i>
            </div>
            <div>
              <p class="text-muted mb-1">Created Slots</p>
              <h3 class="fw-bold mb-0">
                {{ dashboard.created_slots ?? 0 }}
              </h3>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assigned Examinations -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <h5 class="fw-bold mb-3">My Assigned Examinations</h5>

        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Exam ID</th>
                <th>Examination</th>
                <th>Type</th>
                <th>Duration</th>
                <th>Max Marks</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="exam in examinations" :key="exam.id">
                <td>#{{ exam.id }}</td>
                <td>{{ exam.name }}</td>
                <td>{{ exam.exam_type }}</td>
                <td>{{ exam.duration }} min</td>
                <td>{{ exam.max_marks }}</td>
                <td>
                  <span class="badge bg-primary">
                    {{ exam.status }}
                  </span>
                </td>
              </tr>

              <tr v-if="examinations.length === 0">
                <td colspan="6" class="text-center text-muted py-4">
                  No examinations assigned yet
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Examination Slots -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="fw-bold mb-3">My Examination Slots</h5>

        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Slot ID</th>
                <th>Examination ID</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Capacity</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="slot in slots" :key="slot.id">
                <td>#{{ slot.id }}</td>
                <td>{{ slot.examination_id }}</td>
                <td>{{ formatDate(slot.start_time) }}</td>
                <td>{{ formatDate(slot.end_time) }}</td>
                <td>{{ slot.capacity }}</td>
                <td>
                  <span class="badge bg-secondary">
                    {{ slot.status }}
                  </span>
                </td>
              </tr>

              <tr v-if="slots.length === 0">
                <td colspan="6" class="text-center text-muted py-4">
                  No examination slots created yet
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api.js";

const router = useRouter();

const examiner = ref({});
const dashboard = ref({});
const examinations = ref([]);
const slots = ref([]);
const loading = ref(true);
const loggingOut = ref(false);
const error = ref("");

async function loadDashboard() {
  loading.value = true;
  error.value = "";

  try {
    const [dashboardResponse, examsResponse, slotsResponse] =
      await Promise.all([
        api.get("/examiner/dashboard"),
        api.get("/examiner/examinations"),
        api.get("/examiner/slots"),
      ]);

    dashboard.value = dashboardResponse.data;
    examiner.value = dashboardResponse.data.examiner || {};
    examinations.value = examsResponse.data.examinations || [];
    slots.value = slotsResponse.data.slots || [];
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to load examiner dashboard";
  } finally {
    loading.value = false;
  }
}

function formatDate(value) {
  if (!value) return "—";

  // Backend may return a date-time string without a timezone.
  // Display it as supplied rather than accidentally shifting it.
  return String(value).replace("T", " ").slice(0, 19);
}

async function logout() {
  loggingOut.value = true;

  try {
    await api.post("/auth/logout");
    sessionStorage.removeItem("user");
    await router.push("/login");
  } catch (err) {
    error.value =
      err.response?.data?.message || "Logout failed. Please try again.";
  } finally {
    loggingOut.value = false;
  }
}

onMounted(loadDashboard);
</script>

<style scoped>
.stat-icon {
  width: 54px;
  height: 54px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
