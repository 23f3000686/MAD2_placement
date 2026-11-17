
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Student Evaluation</h2>
        <p class="text-muted mb-0">Enter rubric-wise marks and finalize results</p>
      </div>
      <router-link to="/examiner/slots" class="btn btn-outline-secondary">
        Back to Slots
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div v-if="loading" class="text-muted">Loading evaluation...</div>

    <template v-else-if="bookingId && loaded">
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h5>Evaluation Details</h5>
          <p class="mb-1"><strong>Student:</strong> {{ studentName }}</p>
          <p class="mb-1"><strong>Booking ID:</strong> {{ bookingId }}</p>
          <p class="mb-1">
            <strong>Examination ID:</strong> {{ examinationId }}
          </p>
          <p class="mb-1">
            <strong>Status:</strong>
            <span
              class="badge"
              :class="isFinalized ? 'bg-success' : 'bg-warning text-dark'"
            >
              {{ evaluation?.status || "Not Evaluated" }}
            </span>
          </p>
          <p v-if="evaluation" class="mb-0">
            <strong>Saved Total:</strong> {{ evaluation.total_marks }}
          </p>
        </div>
      </div>

      <form @submit.prevent="saveDraft">
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <h5>Rubric-wise Marks</h5>

            <div class="table-responsive">
              <table class="table table-bordered align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Criterion</th>
                    <th>Maximum Marks</th>
                    <th>Weightage</th>
                    <th>Marks Obtained</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="rubric in rubrics" :key="rubric.id">
                    <td>{{ rubric.criterion_name }}</td>
                    <td>{{ rubric.max_marks }}</td>
                    <td>{{ rubric.weightage }}%</td>
                    <td>
                      <input
                        v-model.number="marks[rubric.id]"
                        type="number"
                        class="form-control"
                        min="0"
                        :max="rubric.max_marks"
                        step="any"
                        :disabled="isFinalized"
                        required
                      />
                    </td>
                  </tr>
                  <tr v-if="rubrics.length === 0">
                    <td colspan="4" class="text-center text-muted">
                      No rubrics configured for this examination.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p class="fw-bold text-end mb-0">
              Total: {{ currentTotal }} / {{ maxTotal }}
            </p>
          </div>
        </div>

        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <label class="form-label fw-semibold">Remarks</label>
            <textarea
              v-model="remarks"
              class="form-control"
              rows="4"
              placeholder="Enter evaluation remarks"
              :disabled="isFinalized"
            ></textarea>
          </div>
        </div>

        <div class="d-flex gap-2">
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="saving || isFinalized || rubrics.length === 0"
          >
            {{ saving ? "Saving..." : "Save Draft" }}
          </button>

          <button
            type="button"
            class="btn btn-success"
            :disabled="saving || isFinalized || !evaluation || rubrics.length === 0"
            @click="finalizeEvaluation"
          >
            Finalize Evaluation
          </button>
        </div>
      </form>

      <div v-if="isFinalized" class="alert alert-info mt-4">
        This evaluation is finalized and cannot be edited.
      </div>
    </template>

    <div v-else-if="!bookingId" class="alert alert-info">
      Open an evaluation using the Evaluate button on the Slots page.
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import api from "../services/api";

const route = useRoute();
const bookingId = computed(() => Number(route.query.booking_id) || null);

const rubrics = ref([]);
const marks = ref({});
const remarks = ref("");
const evaluation = ref(null);
const studentName = ref("");
const error = ref("");
const success = ref("");
const loading = ref(false);
const saving = ref(false);
const loaded = ref(false);
const examinationId = ref(null);

const isFinalized = computed(() =>
  evaluation.value?.status === "Finalized" ||
  evaluation.value?.is_published === true
);

const maxTotal = computed(() =>
  rubrics.value.reduce((sum, r) => sum + Number(r.max_marks), 0)
);

const currentTotal = computed(() =>
  rubrics.value.reduce((sum, r) => {
    const value = marks.value[r.id];
    return sum + (value === "" || value == null ? 0 : Number(value) || 0);
  }, 0)
);

function showError(err) {
  error.value = err.response?.data?.message || err.message || "Request failed";
  success.value = "";
}

async function loadEvaluation() {
  if (!bookingId.value) return;

  loading.value = true;
  loaded.value = false;
  error.value = "";

  try {
    const response = await api.get(
      `/examiner/bookings/${bookingId.value}/evaluation`
    );

    const data = response.data;
    examinationId.value = data.examination_id;
    rubrics.value = data.rubrics || [];
    studentName.value = data.student_name || "";
    evaluation.value = data.evaluation;
    remarks.value = data.evaluation?.remarks || "";

    const savedMarks = new Map(
      (data.evaluation?.marks || []).map(m => [m.rubric_id, m.marks_obtained])
    );

    marks.value = Object.fromEntries(
      rubrics.value.map(r => [r.id, savedMarks.get(r.id) ?? ""])
    );

    loaded.value = true;
  } catch (err) {
    showError(err);
  } finally {
    loading.value = false;
  }
}

async function saveDraft() {
  if (isFinalized.value) return;

  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const payload = {
      remarks: remarks.value,
      marks: rubrics.value.map(r => ({
        rubric_id: r.id,
        marks_obtained: Number(marks.value[r.id]),
      })),
    };

    const response = await api.put(
      `/examiner/bookings/${bookingId.value}/evaluation`,
      payload
    );

    evaluation.value = response.data.evaluation;
    success.value = response.data.message || "Draft evaluation saved";
  } catch (err) {
    showError(err);
  } finally {
    saving.value = false;
  }
}

async function finalizeEvaluation() {
  if (!evaluation.value || isFinalized.value) return;

  if (!confirm("Finalize this evaluation? You cannot edit it afterward.")) {
    return;
  }

  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const response = await api.patch(
      `/examiner/bookings/${bookingId.value}/evaluation/finalize`
    );

    evaluation.value = response.data.evaluation;
    success.value = response.data.message || "Evaluation finalized successfully";
  } catch (err) {
    showError(err);
  } finally {
    saving.value = false;
  }
}

onMounted(loadEvaluation);
</script>
