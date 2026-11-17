
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Examiner Assignments</h2>
        <p class="text-muted mb-0">
          Assign examiners to examinations
        </p>
      </div>
      <router-link
        to="/admin/examinations"
        class="btn btn-outline-secondary"
      >
        Back to Examinations
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    <div v-if="success" class="alert alert-success">
      {{ success }}
    </div>

    <!-- Examination Selection -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <label class="form-label fw-semibold">
          Select Examination
        </label>
        <select
          v-model="selectedExamId"
          class="form-select"
          @change="loadAssignments"
        >
          <option value="">Select examination</option>
          <option
            v-for="exam in examinations"
            :key="exam.id"
            :value="exam.id"
          >
            {{ exam.name }} — {{ exam.course_name }}
            ({{ exam.status }})
          </option>
        </select>
      </div>
    </div>

    <template v-if="selectedExam">
      <!-- Assignment Form -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <h5 class="fw-bold mb-3">Assign Examiner</h5>

          <p class="text-muted">
            Examination:
            <strong>{{ selectedExam.name }}</strong>
          </p>

          <div v-if="!canAssign" class="alert alert-warning">
            Assignments cannot be modified for Closed or
            Completed examinations.
          </div>

          <form
            v-else
            class="row g-3 align-items-end"
            @submit.prevent="assignExaminer"
          >
            <div class="col-md-8">
              <label class="form-label">
                Available Examiners
              </label>

              <select
                v-model="selectedExaminerId"
                class="form-select"
                required
              >
                <option value="">Select examiner</option>
                <option
                  v-for="examiner in availableExaminers"
                  :key="examiner.id"
                  :value="examiner.id"
                >
                  {{ examiner.name }} — {{ examiner.email }}
                </option>
              </select>
            </div>

            <div class="col-md-4">
              <button
                type="submit"
                class="btn btn-success w-100"
                :disabled="saving || availableExaminers.length === 0"
              >
                {{ saving ? "Assigning..." : "Assign Examiner" }}
              </button>
            </div>

            <div
              v-if="availableExaminers.length === 0"
              class="col-12 text-muted"
            >
              No additional active examiners are available
              for this examination.
            </div>
          </form>
        </div>
      </div>

      <!-- Existing Assignments -->
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <h5 class="fw-bold mb-3">
            Assigned Examiners ({{ assignments.length }})
          </h5>

          <div v-if="loading" class="text-muted py-3">
            Loading assignments...
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Assignment ID</th>
                  <th>Examiner ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="assignment in assignments"
                  :key="assignment.id"
                >
                  <td>{{ assignment.id }}</td>
                  <td>{{ assignment.examiner_id }}</td>
                  <td>{{ assignment.examiner_name }}</td>
                  <td>{{ assignment.examiner_email }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="assignment.examiner_status === 'active'
                        ? 'bg-success'
                        : 'bg-secondary'"
                    >
                      {{ assignment.examiner_status }}
                    </span>
                  </td>
                  <td>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      :disabled="!canAssign || removingId === assignment.id"
                      @click="removeAssignment(assignment)"
                    >
                      Remove
                    </button>
                  </td>
                </tr>

                <tr v-if="assignments.length === 0">
                  <td
                    colspan="6"
                    class="text-center text-muted py-4"
                  >
                    No examiners assigned yet
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <small class="text-muted">
            An assignment cannot be removed while the
            examiner has examination slots.
          </small>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "../services/api.js";

const route = useRoute();

const examinations = ref([]);
const examiners = ref([]);
const assignments = ref([]);

const selectedExamId = ref("");
const selectedExaminerId = ref("");

const error = ref("");
const success = ref("");

const loading = ref(false);
const saving = ref(false);
const removingId = ref(null);

const selectedExam = computed(() =>
  examinations.value.find(
    exam => exam.id === Number(selectedExamId.value)
  )
);

const canAssign = computed(() =>
  selectedExam.value &&
  !["Closed", "Completed"].includes(selectedExam.value.status)
);

const availableExaminers = computed(() => {
  const assignedIds = new Set(
    assignments.value.map(a => a.examiner_id)
  );

  return examiners.value.filter(
    examiner =>
      examiner.status === "active" &&
      !assignedIds.has(examiner.id)
  );
});

async function loadExaminations() {
  const response = await api.get("/admin/examinations");
  examinations.value = response.data.examinations || [];
}

async function loadExaminers() {
  const response = await api.get("/admin/examiners");
  examiners.value = response.data.examiners || [];
}

async function loadAssignments() {
  error.value = "";
  success.value = "";
  assignments.value = [];
  selectedExaminerId.value = "";

  if (!selectedExamId.value) return;

  loading.value = true;

  try {
    const response = await api.get(
      `/admin/examinations/${selectedExamId.value}/assignments`
    );

    assignments.value = response.data.assignments || [];
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      "Failed to load assignments";
  } finally {
    loading.value = false;
  }
}

async function assignExaminer() {
  if (!selectedExaminerId.value || !canAssign.value) return;

  saving.value = true;
  error.value = "";
  success.value = "";

  try {
    const response = await api.post(
      `/admin/examinations/${selectedExamId.value}/assignments`,
      {
        examiner_id: Number(selectedExaminerId.value)
      }
    );

    await loadAssignments();
    success.value = response.data.message;
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      "Failed to assign examiner";
  } finally {
    saving.value = false;
  }
}

async function removeAssignment(assignment) {
  if (
    !window.confirm(
      `Remove ${assignment.examiner_name} from this examination?`
    )
  ) {
    return;
  }

  removingId.value = assignment.id;
  error.value = "";
  success.value = "";

  try {
    const response = await api.delete(
      `/admin/examinations/${selectedExamId.value}/assignments/${assignment.id}`
    );

    await loadAssignments();
    success.value = response.data.message;
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      "Failed to remove assignment";
  } finally {
    removingId.value = null;
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      loadExaminations(),
      loadExaminers()
    ]);

    const examId = Number(route.query.exam_id);

    if (
      examId &&
      examinations.value.some(exam => exam.id === examId)
    ) {
      selectedExamId.value = examId;
      await loadAssignments();
    }
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      "Failed to load assignment data";
  }
});
</script>
