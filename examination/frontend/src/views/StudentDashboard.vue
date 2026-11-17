
<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Student Dashboard</h2>
        <p class="text-muted mb-0">
          Welcome, {{ student.name || "Student" }}
        </p>
      </div>

      <button class="btn btn-outline-danger" @click="logout">
        <i class="bi bi-box-arrow-right me-2"></i>Logout
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Student Navigation -->
    <div class="row g-3 mb-4">
    <div class="col-md-6">
        <router-link
        to="/student/bookings"
        class="btn btn-primary w-100 py-3"
        >
        <i class="bi bi-calendar-check me-2"></i>
        Book Examination / My Bookings
        </router-link>
    </div>

    <div class="col-md-6">
        <router-link
        to="/student/results"
        class="btn btn-success w-100 py-3"
        >
        <i class="bi bi-award me-2"></i>
        View My Results
        </router-link>
    </div>
    </div>


    <!-- Student Information -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <h5 class="fw-bold mb-3">My Profile</h5>
        <p class="mb-1"><strong>Name:</strong> {{ student.name || "—" }}</p>
        <p class="mb-0"><strong>Email:</strong> {{ student.email || "—" }}</p>
      </div>
    </div>

    <!-- Statistics -->
    <div class="row g-3 mb-4">
      <div
        v-for="item in statistics"
        :key="item.label"
        class="col-md-4"
      >
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center gap-3">
              <div class="stat-icon" :class="item.bg">
                <i class="bi fs-4" :class="item.icon"></i>
              </div>
              <div>
                <p class="text-muted mb-1">{{ item.label }}</p>
                <h3 class="fw-bold mb-0">{{ item.value }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Examinations -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <h5 class="fw-bold mb-3">Examinations</h5>

        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Exam</th>
                <th>Type</th>
                <th>Duration</th>
                <th>Max Marks</th>
                <th>Status</th>
                <th>Booking</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="exam in examinations" :key="exam.id">
                <td>{{ exam.name }}</td>
                <td>{{ exam.exam_type }}</td>
                <td>{{ exam.duration }} min</td>
                <td>{{ exam.max_marks }}</td>
                <td>
                  <span class="badge bg-secondary">
                    {{ exam.status }}
                  </span>
                </td>
                <td>
                  <span
                    class="badge"
                    :class="exam.booking_open ? 'bg-success' : 'bg-warning text-dark'"
                  >
                    {{ exam.booking_open ? "Open" : "Closed" }}
                  </span>
                </td>
              </tr>

              <tr v-if="examinations.length === 0">
                <td colspan="6" class="text-center text-muted py-3">
                  No examinations available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Recent Bookings -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="fw-bold mb-3">My Bookings</h5>

        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Booking ID</th>
                <th>Slot ID</th>
                <th>Status</th>
                <th>Booking Date</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="booking in bookings" :key="booking.id">
                <td>#{{ booking.id }}</td>
                <td>{{ booking.slot_id }}</td>
                <td>
                  <span
                    class="badge"
                    :class="booking.status === 'booked' ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ booking.status }}
                  </span>
                </td>
                <td>{{ formatDate(booking.booking_date) }}</td>
              </tr>

              <tr v-if="bookings.length === 0">
                <td colspan="4" class="text-center text-muted py-3">
                  No bookings yet
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
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api.js";

const router = useRouter();

const student = ref({});
const dashboard = ref({});
const examinations = ref([]);
const bookings = ref([]);
const loading = ref(true);
const error = ref("");

const statistics = computed(() => [
  {
    label: "Total Bookings",
    value: dashboard.value.total_bookings ?? 0,
    icon: "bi-calendar-check",
    bg: "bg-primary-subtle text-primary",
  },
  {
    label: "Active Bookings",
    value: dashboard.value.active_bookings ?? 0,
    icon: "bi-check-circle",
    bg: "bg-success-subtle text-success",
  },
  {
    label: "Cancelled Bookings",
    value: dashboard.value.cancelled_bookings ?? 0,
    icon: "bi-x-circle",
    bg: "bg-danger-subtle text-danger",
  },
]);

async function loadDashboard() {
  loading.value = true;
  error.value = "";

  try {
    const [dashboardResponse, examsResponse, bookingsResponse] =
      await Promise.all([
        api.get("/student/dashboard"),
        api.get("/student/examinations"),
        api.get("/student/bookings"),
      ]);

    dashboard.value = dashboardResponse.data;
    student.value = dashboardResponse.data.student || {};
    examinations.value = examsResponse.data.examinations || [];
    bookings.value = bookingsResponse.data.bookings || [];
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to load student dashboard";
  } finally {
    loading.value = false;
  }
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

async function logout() {
  try {
    await api.post("/auth/logout");
  } catch (err) {
    console.error("Logout failed:", err);
  } finally {
    sessionStorage.removeItem("user");
    router.push("/login");
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
