
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Examination Management</h2>
        <p class="text-muted mb-0">
          Create, schedule and manage examinations
        </p>
      </div>
      <router-link to="/admin/dashboard" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-2"></i>Dashboard
      </router-link>
      
      
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <!-- Search and Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label">Search Examinations</label>
            <input
              v-model="search"
              class="form-control"
              placeholder="Exam name or course"
              @keyup.enter="loadExaminations"
            />
          </div>

          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select v-model="statusFilter" class="form-select">
              <option value="">All Statuses</option>
              <option v-for="s in statuses" :key="s" :value="s">
                {{ s }}
              </option>
            </select>
          </div>

          <div class="col-md-5 d-flex gap-2">
            <button class="btn btn-primary" @click="loadExaminations">
              Search
            </button>
            <button class="btn btn-outline-secondary" @click="clearFilters">
              Clear
            </button>
            <button class="btn btn-success" @click="openAdd">
              <i class="bi bi-plus-lg me-1"></i>Add Exam
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add / Edit Form -->
    <div v-if="showForm" class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0">
          {{ editingId === null ? "Create Examination" : "Edit Examination" }}
        </h5>
      </div>

      <div class="card-body">
        <form @submit.prevent="saveExamination">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Course *</label>
              <select v-model="form.course_id" class="form-select" required>
                <option value="" disabled>Select course</option>
                <option
                  v-for="course in selectableCourses"
                  :key="course.id"
                  :value="course.id"
                >
                  {{ course.code }} — {{ course.name }}
                </option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label">Examination Name *</label>
              <input
                v-model.trim="form.name"
                class="form-control"
                maxlength="100"
                required
              />
            </div>

            <div class="col-md-4">
              <label class="form-label">Examination Type *</label>
              <select v-model="form.exam_type" class="form-select" required>
                <option v-for="type in examTypes" :key="type" :value="type">
                  {{ type }}
                </option>
              </select>
            </div>

            <div class="col-md-4">
              <label class="form-label">Duration (minutes) *</label>
              <input
                v-model.number="form.duration"
                type="number"
                min="1"
                step="1"
                class="form-control"
                required
              />
            </div>

            <div class="col-md-4">
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

            <div class="col-12">
              <h6 class="fw-bold mt-2">Slot Creation Period</h6>
            </div>

            <div class="col-md-6">
              <label class="form-label">Slot Creation Start *</label>
              <input
                v-model="form.slot_creation_start"
                type="datetime-local"
                class="form-control"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">Slot Creation End *</label>
              <input
                v-model="form.slot_creation_end"
                type="datetime-local"
                class="form-control"
                required
              />
            </div>

            <div class="col-12">
              <h6 class="fw-bold mt-2">Student Booking Period</h6>
            </div>

            <div class="col-md-6">
              <label class="form-label">Booking Start *</label>
              <input
                v-model="form.booking_start"
                type="datetime-local"
                class="form-control"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">Booking End *</label>
              <input
                v-model="form.booking_end"
                type="datetime-local"
                class="form-control"
                required
              />
            </div>

            <div class="col-12">
              <small class="text-muted">
                All dates and times are entered in Indian Standard Time (IST).
                Slot creation must end before student booking begins.
                New examinations start in Draft status.
              </small>
            </div>
          </div>

          <div class="d-flex gap-2 mt-4">
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "Saving..." : editingId === null ? "Create Examination" : "Update Examination" }}
            </button>
            <button type="button" class="btn btn-secondary" @click="showForm = false">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Examination Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="fw-bold mb-3">
          Examinations ({{ examinations.length }})
        </h5>

        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Examination</th>
                <th>Course</th>
                <th>Type</th>
                <th>Duration</th>
                <th>Marks</th>
                <th>Booking Period (IST)</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="exam in examinations" :key="exam.id">
                <td>#{{ exam.id }}</td>
                <td class="fw-semibold">{{ exam.name }}</td>
                <td>{{ exam.course_name }}</td>
                <td>{{ exam.exam_type }}</td>
                <td>{{ exam.duration }} min</td>
                <td>{{ exam.max_marks }}</td>
                <td>
                  <small>
                    {{ formatIST(exam.booking_start) }}
                    <div class="text-muted">to</div>
                    {{ formatIST(exam.booking_end) }}
                  </small>
                </td>
                <td>
                  <span class="badge" :class="statusClass(exam.status)">
                    {{ exam.status }}
                  </span>
                </td>
                <td>
                  <div class="d-flex flex-wrap gap-1">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      :disabled="exam.status === 'Completed'"
                      @click="openEdit(exam)"
                    >
                    <router-link
                        :to="{ path: '/admin/rubrics', query: { exam_id: exam.id } }"
                        class="btn btn-sm btn-outline-info"
                        >
                        Rubrics
                        </router-link>
                    <router-link
                        :to="{
                            path: '/admin/assignments',
                            query: { exam_id: exam.id }
                        }"
                        class="btn btn-sm btn-outline-secondary"
                        >
                        Assign Examiners
                    </router-link>
                      Edit
                    </button>

                    <button
                      class="btn btn-sm btn-outline-success"
                      :disabled="nextStatuses(exam.status).length === 0"
                      @click="openStatus(exam)"
                    >
                      Status
                    </button>

                    <button
                      v-if="exam.status === 'Draft'"
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteExamination(exam)"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="examinations.length === 0">
                <td colspan="9" class="text-center text-muted py-4">
                  No examinations found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Status Change Panel -->
    <div v-if="selectedExam" class="card border-0 shadow-sm mt-4">
      <div class="card-body">
        <h5 class="fw-bold">Change Examination Status</h5>
        <p class="text-muted">
          {{ selectedExam.name }} — Current: {{ selectedExam.status }}
        </p>

        <div class="d-flex flex-wrap gap-2">
          <button
            v-for="s in nextStatuses(selectedExam.status)"
            :key="s"
            class="btn btn-outline-primary"
            :disabled="savingStatus"
            @click="changeStatus(s)"
          >
            Move to {{ s }}
          </button>

          <button class="btn btn-secondary" @click="selectedExam = null">
            Cancel
          </button>
        </div>

        <small class="text-muted d-block mt-3">
          Status changes are subject to backend scheduling rules.
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api.js";

const examTypes = ["Viva", "Practical", "Project Demo", "Assessment"];
const statuses = ["Draft", "Slot Creation", "Booking Open", "Closed", "Completed"];

const transitions = {
  Draft: ["Slot Creation"],
  "Slot Creation": ["Booking Open", "Closed"],
  "Booking Open": ["Closed"],
  Closed: ["Completed"],
  Completed: [],
};

const examinations = ref([]);
const courses = ref([]);
const search = ref("");
const statusFilter = ref("");
const error = ref("");
const success = ref("");
const loading = ref(false);
const saving = ref(false);
const savingStatus = ref(false);
const showForm = ref(false);
const editingId = ref(null);
const selectedExam = ref(null);

const emptyForm = () => ({
  course_id: "",
  name: "",
  exam_type: "Viva",
  duration: 30,
  max_marks: 100,
  slot_creation_start: "",
  slot_creation_end: "",
  booking_start: "",
  booking_end: "",
});

const form = ref(emptyForm());

const selectableCourses = computed(() =>
  courses.value.filter(
    c => c.status === "active" || c.id === form.value.course_id
  )
);

// Backend returns naive UTC. Convert to IST for editing.
function toISTInput(value) {
  if (!value) return "";
  const utc = new Date(value.endsWith("Z") ? value : `${value}Z`);
  if (Number.isNaN(utc.getTime())) return "";
  return new Date(utc.getTime() + 330 * 60000)
    .toISOString()
    .slice(0, 16);
}

function formatIST(value) {
  if (!value) return "—";
  const input = toISTInput(value);
  return input ? input.replace("T", " ") : "—";
}

function statusClass(status) {
  return {
    Draft: "bg-secondary",
    "Slot Creation": "bg-info text-dark",
    "Booking Open": "bg-success",
    Closed: "bg-warning text-dark",
    Completed: "bg-primary",
  }[status] || "bg-secondary";
}

function nextStatuses(status) {
  return transitions[status] || [];
}

async function loadCourses() {
  const response = await api.get("/admin/courses");
  courses.value = response.data.courses || [];
}

async function loadExaminations() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/admin/examinations", {
      params: {
        search: search.value,
        status: statusFilter.value,
      },
    });

    examinations.value = response.data.examinations || [];
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load examinations";
  } finally {
    loading.value = false;
  }
}

function clearFilters() {
  search.value = "";
  statusFilter.value = "";
  loadExaminations();
}

function openAdd() {
  editingId.value = null;
  form.value = emptyForm();
  selectedExam.value = null;
  showForm.value = true;
  error.value = "";
  success.value = "";
}

function openEdit(exam) {
  editingId.value = exam.id;
  form.value = {
    course_id: exam.course_id,
    name: exam.name,
    exam_type: exam.exam_type,
    duration: exam.duration,
    max_marks: exam.max_marks,
    slot_creation_start: toISTInput(exam.slot_creation_start),
    slot_creation_end: toISTInput(exam.slot_creation_end),
    booking_start: toISTInput(exam.booking_start),
    booking_end: toISTInput(exam.booking_end),
  };

  selectedExam.value = null;
  showForm.value = true;
  error.value = "";
  success.value = "";
}

async function saveExamination() {
  error.value = "";
  success.value = "";

  const f = form.value;

  if (
    !f.slot_creation_start ||
    !f.slot_creation_end ||
    !f.booking_start ||
    !f.booking_end
  ) {
    error.value = "All scheduling dates are required";
    return;
  }

  if (
    f.slot_creation_start >= f.slot_creation_end ||
    f.booking_start >= f.booking_end ||
    f.slot_creation_end > f.booking_start
  ) {
    error.value = "Invalid scheduling timeline";
    return;
  }

  saving.value = true;

  try {
    const payload = {
      ...f,
      course_id: Number(f.course_id),
      duration: Number(f.duration),
      max_marks: Number(f.max_marks),
    };

    if (editingId.value === null) {
      await api.post("/admin/examinations", {
        ...payload,
        status: "Draft",
      });
      success.value = "Examination created successfully";
    } else {
      await api.put(`/admin/examinations/${editingId.value}`, payload);
      success.value = "Examination updated successfully";
    }

    showForm.value = false;
    await loadExaminations();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to save examination";
  } finally {
    saving.value = false;
  }
}

async function deleteExamination(exam) {
  if (!window.confirm(`Delete examination "${exam.name}"?`)) return;

  error.value = "";
  success.value = "";

  try {
    await api.delete(`/admin/examinations/${exam.id}`);
    success.value = "Examination deleted successfully";
    await loadExaminations();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to delete examination";
  }
}

function openStatus(exam) {
  selectedExam.value = exam;
  showForm.value = false;
  error.value = "";
  success.value = "";
}

async function changeStatus(status) {
  savingStatus.value = true;
  error.value = "";
  success.value = "";

  try {
    await api.patch(
      `/admin/examinations/${selectedExam.value.id}/status`,
      { status }
    );

    success.value = `Examination status changed to ${status}`;
    selectedExam.value = null;
    await loadExaminations();
  } catch (err) {
    error.value = err.response?.data?.message || "Status change failed";
  } finally {
    savingStatus.value = false;
  }
}

onMounted(async () => {
  try {
    await loadCourses();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load courses";
  }

  await loadExaminations();
});
</script>
