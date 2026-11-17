
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Admin Results Management</h2>
        <p class="text-muted mb-0">
          Review evaluations and publish examination results
        </p>
      </div>
      <router-link
        to="/admin/dashboard"
        class="btn btn-outline-secondary"
      >
        Back to Dashboard
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
      <div v-if="incompleteIds.length">
        Incomplete IDs: {{ incompleteIds.join(", ") }}
      </div>
    </div>

    <div v-if="success" class="alert alert-success">
      {{ success }}
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <label class="form-label fw-bold">Select Examination</label>
        <select
          v-model="selectedExamId"
          class="form-select"
          @change="loadResults"
        >
          <option value="">Choose an examination</option>
          <option
            v-for="exam in examinations"
            :key="exam.id"
            :value="exam.id"
          >
            {{ exam.name }} ({{ exam.status }})
          </option>
        </select>
      </div>
    </div>

    <div v-if="selectedExamId" class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="mb-0">{{ examinationName }}</h5>
          <button
            class="btn btn-success"
            :disabled="loading || publishing || !canPublish"
            @click="publishResults"
          >
            {{ publishing ? "Publishing..." : "Publish Results" }}
          </button>
        </div>

        <p class="text-muted">
          All active bookings must have finalized evaluations before
          results can be published.
        </p>

        <div v-if="loading">Loading results...</div>

        <div v-else class="table-responsive">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Evaluation ID</th>
                <th>Booking ID</th>
                <th>Student</th>
                <th>Marks</th>
                <th>Status</th>
                <th>Published</th>
                <th>Remarks</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="result in results"
                :key="result.evaluation_id"
              >
                <td>{{ result.evaluation_id }}</td>
                <td>{{ result.booking_id }}</td>
                <td>
                  {{ result.student_name }}
                  <div class="small text-muted">
                    {{ result.student_email }}
                  </div>
                </td>
                <td>{{ result.total_marks }}</td>
                <td>
                  <span
                    class="badge"
                    :class="result.status === 'Finalized'
                      ? 'bg-success'
                      : 'bg-warning text-dark'"
                  >
                    {{ result.status }}
                  </span>
                </td>
                <td>
                  <span
                    class="badge"
                    :class="result.is_published
                      ? 'bg-success'
                      : 'bg-secondary'"
                  >
                    {{ result.is_published ? "Yes" : "No" }}
                  </span>
                </td>
                <td>{{ result.remarks || "-" }}</td>
              </tr>

              <tr v-if="results.length === 0">
                <td colspan="7" class="text-center text-muted">
                  No evaluations available for this examination.
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
import { useRoute } from "vue-router";
import api from "../services/api";

const route = useRoute();

const examinations = ref([]);
const selectedExamId = ref("");
const examinationName = ref("");
const results = ref([]);
const loading = ref(false);
const publishing = ref(false);
const error = ref("");
const success = ref("");
const incompleteIds = ref([]);

const canPublish = computed(() =>
  results.value.length > 0 &&
  results.value.every(
    (result) => result.status === "Finalized"
  ) &&
  results.value.some(
    (result) => !result.is_published
  )
);

function showError(err) {
  error.value =
    err.response?.data?.message ||
    err.message ||
    "Request failed";

  incompleteIds.value =
    err.response?.data?.incomplete_booking_ids ||
    err.response?.data?.incomplete_evaluation_ids ||
    [];
}

async function loadExaminations() {
  try {
    const response = await api.get("/admin/examinations");
    examinations.value = response.data.examinations || [];

    const queryId = Number(route.query.exam_id);

    if (
      queryId &&
      examinations.value.some((exam) => exam.id === queryId)
    ) {
      selectedExamId.value = queryId;
      await loadResults();
    }
  } catch (err) {
    showError(err);
  }
}

async function loadResults() {
  results.value = [];
  examinationName.value = "";
  error.value = "";
  success.value = "";
  incompleteIds.value = [];

  if (!selectedExamId.value) return;

  loading.value = true;

  try {
    const response = await api.get(
      `/admin/examinations/${selectedExamId.value}/results`
    );

    examinationName.value = response.data.examination_name;
    results.value = response.data.results || [];
  } catch (err) {
    showError(err);
  } finally {
    loading.value = false;
  }
}

async function publishResults() {
  if (!confirm("Publish all finalized results for this examination?")) {
    return;
  }

  publishing.value = true;
  error.value = "";
  success.value = "";
  incompleteIds.value = [];

  try {
    const response = await api.patch(
      `/admin/examinations/${selectedExamId.value}/results/publish`
    );

    await loadResults();
    success.value =
      response.data.message || "Results published successfully";
  } catch (err) {
    showError(err);
  } finally {
    publishing.value = false;
  }
}

onMounted(loadExaminations);
</script>
