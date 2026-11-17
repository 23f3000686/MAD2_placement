
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Rubric Management</h2>
        <p class="text-muted mb-0">
          Configure evaluation criteria and marking weightages
        </p>
      </div>
      <router-link to="/admin/examinations" class="btn btn-outline-secondary">
        Back to Examinations
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <!-- Examination Selection -->
    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <label class="form-label fw-semibold">Select Examination</label>
        <select
          v-model="selectedExamId"
          class="form-select"
          @change="loadRubrics"
        >
          <option value="">Select examination</option>
          <option v-for="exam in examinations" :key="exam.id" :value="exam.id">
            {{ exam.name }} — {{ exam.course_name }} ({{ exam.status }})
          </option>
        </select>
      </div>
    </div>

    <template v-if="summary">
      <!-- Summary Cards -->
      <div class="row g-3 mb-4">
        <div class="col-md-3" v-for="card in summaryCards" :key="card.label">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <small class="text-muted">{{ card.label }}</small>
              <h3 class="fw-bold mt-2">{{ card.value }}</h3>
            </div>
          </div>
        </div>
      </div>

      <div
        class="alert"
        :class="summary.is_complete ? 'alert-success' : 'alert-warning'"
      >
        {{
          summary.is_complete
            ? "Rubric configuration is complete."
            : "Rubric configuration is incomplete. Total marks and weightage must match the examination maximum and 100%."
        }}
      </div>

      <!-- Add / Edit Form -->
      <div v-if="canManage" class="mb-3">
        <button
          v-if="!showForm"
          class="btn btn-success"
          @click="openAdd"
        >
          <i class="bi bi-plus-lg me-1"></i>Add Criterion
        </button>
      </div>

      <div v-if="showForm" class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-white">
          <h5 class="mb-0">
            {{ editingId === null ? "Add Rubric Criterion" : "Edit Rubric Criterion" }}
          </h5>
        </div>

        <div class="card-body">
          <form @submit.prevent="saveRubric">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Criterion Name *</label>
                <input
                  v-model.trim="form.criterion_name"
                  class="form-control"
                  maxlength="100"
                  required
                />
              </div>

              <div class="col-md-3">
                <label class="form-label">Maximum Marks *</label>
                <input
                  v-model.number="form.max_marks"
                  type="number"
                  min="1"
                  step="1"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-3">
                <label class="form-label">Weightage (%) *</label>
                <input
                  v-model.number="form.weightage"
                  type="number"
                  min="0.01"
                  max="100"
                  step="any"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-12">
                <label class="form-label">Description</label>
                <textarea
                  v-model="form.description"
                  class="form-control"
                  maxlength="1000"
                  rows="3"
                ></textarea>
              </div>
            </div>

            <div class="d-flex gap-2 mt-3">
              <button class="btn btn-primary" :disabled="saving">
                {{ saving ? "Saving..." : editingId === null ? "Add Criterion" : "Update Criterion" }}
              </button>
              <button
                type="button"
                class="btn btn-secondary"
                @click="showForm = false"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Rubric Table -->
      <div class="card shadow-sm border-0">
        <div class="card-body">
          <h5 class="fw-bold mb-3">Evaluation Criteria</h5>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Criterion</th>
                  <th>Description</th>
                  <th>Max Marks</th>
                  <th>Weightage</th>
                  <th v-if="canManage">Actions</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="rubric in summary.rubrics" :key="rubric.id">
                  <td>{{ rubric.id }}</td>
                  <td class="fw-semibold">{{ rubric.criterion_name }}</td>
                  <td>{{ rubric.description || "—" }}</td>
                  <td>{{ rubric.max_marks }}</td>
                  <td>{{ rubric.weightage }}%</td>
                  <td v-if="canManage">
                    <div class="d-flex gap-2">
                      <button
                        class="btn btn-sm btn-outline-primary"
                        @click="openEdit(rubric)"
                      >
                        Edit
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        @click="deleteRubric(rubric)"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>

                <tr v-if="summary.rubrics.length === 0">
                  <td
                    :colspan="canManage ? 6 : 5"
                    class="text-center text-muted py-4"
                  >
                    No rubric criteria added yet
                  </td>
                </tr>
              </tbody>

              <tfoot class="table-light">
                <tr class="fw-bold">
                  <td colspan="3">Total</td>
                  <td>{{ summary.total_rubric_marks }}</td>
                  <td>{{ summary.total_weightage }}%</td>
                  <td v-if="canManage"></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <p v-if="!canManage" class="text-muted small mb-0">
            This examination's current status does not allow rubric changes.
            The backend also prevents changes after evaluations exist.
          </p>
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
const selectedExamId = ref("");
const summary = ref(null);
const error = ref("");
const success = ref("");
const saving = ref(false);
const showForm = ref(false);
const editingId = ref(null);

const emptyForm = () => ({
  criterion_name: "",
  max_marks: 1,
  weightage: 1,
  description: "",
});

const form = ref(emptyForm());

const selectedExam = computed(() =>
  examinations.value.find(e => e.id === Number(selectedExamId.value))
);

const canManage = computed(() =>
  ["Draft", "Slot Creation"].includes(selectedExam.value?.status)
);

const summaryCards = computed(() => {
  if (!summary.value) return [];

  return [
    {
      label: "Examination Max Marks",
      value: summary.value.examination_max_marks,
    },
    {
      label: "Assigned Rubric Marks",
      value: summary.value.total_rubric_marks,
    },
    {
      label: "Remaining Marks",
      value: summary.value.remaining_marks,
    },
    {
      label: "Remaining Weightage",
      value: `${summary.value.remaining_weightage}%`,
    },
  ];
});

async function loadExaminations() {
  const response = await api.get("/admin/examinations");
  examinations.value = response.data.examinations || [];
}

async function loadRubrics() {
  error.value = "";
  success.value = "";
  summary.value = null;
  showForm.value = false;
  editingId.value = null;

  if (!selectedExamId.value) return;

  try {
    const response = await api.get(
      `/admin/examinations/${selectedExamId.value}/rubrics`
    );
    summary.value = response.data;
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load rubrics";
  }
}

function openAdd() {
  editingId.value = null;
  form.value = emptyForm();
  showForm.value = true;
  error.value = "";
  success.value = "";
}

function openEdit(rubric) {
  editingId.value = rubric.id;
  form.value = {
    criterion_name: rubric.criterion_name,
    max_marks: rubric.max_marks,
    weightage: rubric.weightage,
    description: rubric.description || "",
  };
  showForm.value = true;
  error.value = "";
  success.value = "";
}

async function saveRubric() {
  error.value = "";
  success.value = "";
  saving.value = true;

  const examId = selectedExamId.value;

  try {
    const payload = {
      ...form.value,
      max_marks: Number(form.value.max_marks),
      weightage: Number(form.value.weightage),
    };

    let response;

    if (editingId.value === null) {
      response = await api.post(
        `/admin/examinations/${examId}/rubrics`,
        payload
      );
    } else {
      response = await api.put(
        `/admin/examinations/${examId}/rubrics/${editingId.value}`,
        payload
      );
    }

    summary.value = response.data.summary;
    success.value = response.data.message;
    showForm.value = false;
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to save rubric";
  } finally {
    saving.value = false;
  }
}

async function deleteRubric(rubric) {
  if (!window.confirm(`Delete criterion "${rubric.criterion_name}"?`)) return;

  error.value = "";
  success.value = "";

  try {
    const response = await api.delete(
      `/admin/examinations/${selectedExamId.value}/rubrics/${rubric.id}`
    );

    summary.value = response.data.summary;
    success.value = response.data.message;
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to delete rubric";
  }
}

onMounted(async () => {
  try {
    await loadExaminations();

    const examId = Number(route.query.exam_id);

    if (examId && examinations.value.some(e => e.id === examId)) {
      selectedExamId.value = examId;
      await loadRubrics();
    }
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load examinations";
  }
});
</script>
