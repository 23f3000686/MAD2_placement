
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">My Examination Results</h2>
        <p class="text-muted mb-0">
          View your published examination results
        </p>
      </div>

      <router-link
        to="/student/dashboard"
        class="btn btn-outline-secondary"
      >
        Back to Dashboard
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="loading" class="text-center py-4">
      Loading results...
    </div>

    <template v-else>
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h5>Student Information</h5>
          <p class="mb-1">
            <strong>Name:</strong> {{ studentName || "-" }}
          </p>
          <p class="mb-0">
            <strong>Published Results:</strong> {{ results.length }}
          </p>
        </div>
      </div>

      <div v-if="results.length === 0" class="alert alert-info">
        No published examination results are available yet.
      </div>

      <div
        v-for="result in results"
        :key="result.evaluation_id"
        class="card shadow-sm mb-4"
      >
        <div class="card-header bg-light">
          <h5 class="mb-0">{{ result.examination_name }}</h5>
        </div>

        <div class="card-body">
          <div class="row mb-3">
            <div class="col-md-4">
              <strong>Booking ID:</strong> {{ result.booking_id }}
            </div>

            <div class="col-md-4">
              <strong>Total Marks:</strong>
              {{ result.total_marks }} / {{ result.maximum_marks }}
            </div>

            <div class="col-md-4">
              <strong>Percentage:</strong>
              {{ percentage(result) }}%
            </div>
          </div>

          <p>
            <strong>Evaluation Date:</strong>
            {{ formatDate(result.evaluation_date) }}
          </p>

          <h6 class="fw-bold mt-4">Rubric-wise Marks</h6>

          <div class="table-responsive">
            <table class="table table-bordered">
              <thead class="table-light">
                <tr>
                  <th>Criterion</th>
                  <th>Maximum Marks</th>
                  <th>Marks Obtained</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="mark in result.rubric_marks"
                  :key="mark.rubric_id"
                >
                  <td>{{ mark.criterion_name }}</td>
                  <td>{{ mark.maximum_marks }}</td>
                  <td>{{ mark.marks_obtained }}</td>
                </tr>

                <tr v-if="!result.rubric_marks?.length">
                  <td colspan="3" class="text-center text-muted">
                    No rubric details available.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mt-3">
            <strong>Examiner Remarks:</strong>
            <p class="mb-0">{{ result.remarks || "No remarks provided." }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";

const studentName = ref("");
const results = ref([]);
const loading = ref(false);
const error = ref("");

function formatDate(value) {
  if (!value) return "-";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString("en-IN");
}

function percentage(result) {
  const maximum = Number(result.maximum_marks);
  const obtained = Number(result.total_marks);

  if (!maximum || !Number.isFinite(obtained)) return "0.00";

  return ((obtained / maximum) * 100).toFixed(2);
}

async function loadResults() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/student/results");

    studentName.value = response.data.student_name || "";
    results.value = response.data.results || [];
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      "Unable to load examination results.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadResults);
</script>
