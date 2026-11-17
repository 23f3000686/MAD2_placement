
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Examiner Slot Management</h2>
        <p class="text-muted">Create and manage examination slots</p>
      </div>
      <router-link to="/examiner/dashboard" class="btn btn-outline-secondary">
        Back to Dashboard
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5>{{ editingId ? "Edit Slot" : "Create Slot" }}</h5>

        <form @submit.prevent="saveSlot">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Examination</label>
              <select
                v-model="form.examination_id"
                class="form-select"
                :disabled="!!editingId"
                required
              >
                <option value="">Select Examination</option>
                <option
                  v-for="exam in examinations"
                  :key="exam.id"
                  :value="exam.id"
                >
                  {{ exam.name }} ({{ exam.status }})
                </option>
              </select>
            </div>

            <div class="col-md-3">
              <label class="form-label">Start Time (IST)</label>
              <input
                v-model="form.start_time"
                type="datetime-local"
                class="form-control"
                required
              />
            </div>

            <div class="col-md-3">
              <label class="form-label">End Time (IST)</label>
              <input
                v-model="form.end_time"
                type="datetime-local"
                class="form-control"
                required
              />
            </div>

            <div class="col-md-4">
              <label class="form-label">Capacity</label>
              <input
                v-model.number="form.capacity"
                type="number"
                min="1"
                step="1"
                class="form-control"
                required
              />
            </div>

            <div class="col-md-5">
              <label class="form-label">Meeting Link (Optional)</label>
              <input
                v-model="form.meeting_link"
                type="url"
                maxlength="500"
                class="form-control"
                placeholder="https://meet.example.com/..."
              />
            </div>

            <div class="col-md-3">
              <label class="form-label">Status</label>
              <select v-model="form.status" class="form-select">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div class="mt-3 d-flex gap-2">
            <button class="btn btn-primary" :disabled="saving">
              {{ saving ? "Saving..." : editingId ? "Update Slot" : "Create Slot" }}
            </button>
            <button
              v-if="editingId"
              type="button"
              class="btn btn-secondary"
              @click="resetForm"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <h5>My Slots ({{ slots.length }})</h5>

        <div class="table-responsive">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Examination</th>
                <th>Start (IST)</th>
                <th>End (IST)</th>
                <th>Capacity</th>
                <th>Booked</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="slot in slots" :key="slot.id">
                <td>{{ slot.id }}</td>
                <td>{{ examName(slot.examination_id) }}</td>
                <td>{{ formatDate(slot.start_time) }}</td>
                <td>{{ formatDate(slot.end_time) }}</td>
                <td>{{ slot.capacity }}</td>
                <td>{{ slot.booked_count }}</td>
                <td>
                  <span
                    class="badge"
                    :class="slot.status === 'active' ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ slot.status }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="editSlot(slot)"
                    >
                      Edit
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      @click="deleteSlot(slot)"
                    >
                      Delete
                    </button>
                    <button
                      class="btn btn-sm btn-outline-info"
                      @click="viewStudents(slot)"
                    >
                      Students
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="slots.length === 0">
                <td colspan="8" class="text-center text-muted">
                  No slots created yet.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="selectedSlot" class="card shadow-sm mt-4">
      <div class="card-body">
        <div class="d-flex justify-content-between">
          <h5>Students for Slot #{{ selectedSlot.id }}</h5>
          <button class="btn btn-sm btn-secondary" @click="selectedSlot = null">
            Close
          </button>
        </div>
        
    <div class="table-responsive">
    <table class="table table-bordered table-hover align-middle mt-3">
        <thead class="table-light">
        <tr>
            <th>Booking ID</th>
            <th>Student Name</th>
            <th>Email</th>
            <th>Evaluation Status</th>
            <th>Action</th>
        </tr>
        </thead>

        <tbody>
        <tr v-for="student in students" :key="student.booking_id">
            <td>{{ student.booking_id }}</td>
            <td>{{ student.student_name }}</td>
            <td>{{ student.student_email }}</td>
            <td>
            <span
                class="badge"
                :class="student.evaluation_status === 'Finalized'
                ? 'bg-success'
                : 'bg-warning text-dark'"
            >
                {{ student.evaluation_status || 'Not Evaluated' }}
            </span>
            </td>
            <td>
            <router-link
                :to="{
                path: '/examiner/evaluations',
                query: { booking_id: student.booking_id }
                }"
                class="btn btn-sm btn-outline-primary"
            >
                {{ student.evaluation_status === 'Finalized' ? 'View Evaluation' : 'Evaluate' }}
            </router-link>
            </td>
        </tr>

        <tr v-if="students.length === 0">
            <td colspan="5" class="text-center text-muted">
            No students have booked this slot.
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
import api from "../services/api";

const examinations = ref([]);
const slots = ref([]);
const error = ref("");
const success = ref("");
const saving = ref(false);
const editingId = ref(null);
const selectedSlot = ref(null);
const students = ref([]);

const emptyForm = () => ({
  examination_id: "",
  start_time: "",
  end_time: "",
  capacity: 1,
  meeting_link: "",
  status: "active",
});

const form = ref(emptyForm());

function showError(err) {
  error.value = err.response?.data?.message || err.message || "Something went wrong";
  success.value = "";
}

function resetForm() {
  editingId.value = null;
  form.value = emptyForm();
}

function examName(id) {
  return examinations.value.find(e => e.id === id)?.name || `Exam #${id}`;
}

function formatDate(value) {
  return value ? value.replace("T", " ").slice(0, 16) : "-";
}

async function loadData() {
  try {
    const [examRes, slotRes] = await Promise.all([
      api.get("/examiner/examinations"),
      api.get("/examiner/slots"),
    ]);

    examinations.value = examRes.data.examinations || [];
    slots.value = slotRes.data.slots || [];
  } catch (err) {
    showError(err);
  }
}

async function saveSlot() {
  error.value = "";
  success.value = "";
  saving.value = true;

  try {
    const payload = {
      ...form.value,
      meeting_link: form.value.meeting_link || null,
    };

    if (editingId.value) {
      await api.put(`/examiner/slots/${editingId.value}`, payload);
      success.value = "Slot updated successfully";
    } else {
      await api.post("/examiner/slots", payload);
      success.value = "Slot created successfully";
    }

    resetForm();
    await loadData();
  } catch (err) {
    showError(err);
  } finally {
    saving.value = false;
  }
}

function editSlot(slot) {
  error.value = "";
  success.value = "";
  editingId.value = slot.id;
  form.value = {
    examination_id: slot.examination_id,
    start_time: slot.start_time?.slice(0, 16) || "",
    end_time: slot.end_time?.slice(0, 16) || "",
    capacity: slot.capacity,
    meeting_link: slot.meeting_link || "",
    status: slot.status,
  };
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function deleteSlot(slot) {
  if (!confirm(`Delete slot #${slot.id}?`)) return;

  error.value = "";
  success.value = "";

  try {
    await api.delete(`/examiner/slots/${slot.id}`);
    success.value = "Slot deleted successfully";
    await loadData();
  } catch (err) {
    showError(err);
  }
}

async function viewStudents(slot) {
  error.value = "";

  try {
    const response = await api.get(`/examiner/slots/${slot.id}/students`);
    selectedSlot.value = slot;
    students.value = response.data.students || [];
  } catch (err) {
    showError(err);
  }
}

onMounted(loadData);
</script>
