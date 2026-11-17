
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Examiner Management</h2>
        <p class="text-muted mb-0">Manage examiner accounts and access</p>
      </div>
      <router-link to="/admin/dashboard" class="btn btn-outline-secondary">
        Back to Dashboard
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-5">
            <label class="form-label">Search Examiner</label>
            <input v-model="search" class="form-control"
              placeholder="Name, email or department"
              @keyup.enter="loadExaminers" />
          </div>
          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select v-model="statusFilter" class="form-select">
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="col-md-4 d-flex gap-2">
            <button class="btn btn-primary" @click="loadExaminers">Search</button>
            <button class="btn btn-outline-secondary" @click="clearFilters">Clear</button>
            <button class="btn btn-success" @click="openAdd">Add Examiner</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <h5>{{ editingId === null ? "Add Examiner" : "Edit Examiner" }}</h5>
        <form @submit.prevent="saveExaminer">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Full Name *</label>
              <input v-model.trim="form.name" maxlength="100"
                class="form-control" required />
            </div>
            <div class="col-md-6">
              <label class="form-label">Email *</label>
              <input v-model.trim="form.email" type="email"
                class="form-control" required />
            </div>
            <div class="col-md-6">
              <label class="form-label">Department</label>
              <input v-model.trim="form.department" maxlength="100"
                class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Contact</label>
              <input v-model.trim="form.contact" maxlength="30"
                class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label">
                Password {{ editingId === null ? "*" : "(leave blank to keep existing)" }}
              </label>
              <input v-model="form.password" type="password"
                minlength="8" class="form-control"
                :required="editingId === null" />
            </div>
          </div>
          <div class="d-flex gap-2 mt-3">
            <button class="btn btn-primary" :disabled="saving">
              {{ saving ? "Saving..." : "Save Examiner" }}
            </button>
            <button type="button" class="btn btn-secondary"
              @click="showForm = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="mb-3">Examiners ({{ examiners.length }})</h5>
        <div v-if="loading" class="text-center py-4">Loading...</div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th><th>Name</th><th>Email</th>
                <th>Department</th><th>Contact</th>
                <th>Status</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="examiner in examiners" :key="examiner.id">
                <td>{{ examiner.id }}</td>
                <td>{{ examiner.name }}</td>
                <td>{{ examiner.email }}</td>
                <td>{{ examiner.department || "—" }}</td>
                <td>{{ examiner.contact || "—" }}</td>
                <td>
                  <span class="badge"
                    :class="examiner.status === 'active' ? 'bg-success' : 'bg-secondary'">
                    {{ examiner.status }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-outline-primary"
                      @click="openEdit(examiner)">Edit</button>
                    <button class="btn btn-sm"
                      :class="examiner.status === 'active' ? 'btn-outline-warning' : 'btn-outline-success'"
                      @click="toggleStatus(examiner)">
                      {{ examiner.status === "active" ? "Deactivate" : "Activate" }}
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="examiners.length === 0">
                <td colspan="7" class="text-center text-muted py-4">
                  No examiners found
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
import api from "../services/api.js";

const examiners = ref([]);
const search = ref("");
const statusFilter = ref("");
const error = ref("");
const success = ref("");
const loading = ref(false);
const saving = ref(false);
const showForm = ref(false);
const editingId = ref(null);

const emptyForm = () => ({
  name: "", email: "", department: "", contact: "", password: ""
});
const form = ref(emptyForm());

async function loadExaminers() {
  loading.value = true;
  error.value = "";
  try {
    const response = await api.get("/admin/examiners", {
      params: { search: search.value, status: statusFilter.value }
    });
    examiners.value = response.data.examiners || [];
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load examiners";
  } finally {
    loading.value = false;
  }
}

function clearFilters() {
  search.value = "";
  statusFilter.value = "";
  loadExaminers();
}

function openAdd() {
  editingId.value = null;
  form.value = emptyForm();
  showForm.value = true;
  error.value = "";
  success.value = "";
}

function openEdit(examiner) {
  editingId.value = examiner.id;
  form.value = {
    name: examiner.name,
    email: examiner.email,
    department: examiner.department || "",
    contact: examiner.contact || "",
    password: ""
  };
  showForm.value = true;
  error.value = "";
  success.value = "";
}

async function saveExaminer() {
  saving.value = true;
  error.value = "";
  success.value = "";
  try {
    const payload = { ...form.value };
    if (editingId.value !== null && !payload.password) {
      delete payload.password;
    }

    let response;
    if (editingId.value === null) {
      response = await api.post("/admin/examiners", payload);
    } else {
      response = await api.put(`/admin/examiners/${editingId.value}`, payload);
    }

    success.value = response.data.message;
    showForm.value = false;
    await loadExaminers();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to save examiner";
  } finally {
    saving.value = false;
  }
}

async function toggleStatus(examiner) {
  const newStatus = examiner.status === "active" ? "inactive" : "active";
  if (!window.confirm(`Change ${examiner.name} to ${newStatus}?`)) return;

  error.value = "";
  success.value = "";
  try {
    const response = await api.patch(
      `/admin/examiners/${examiner.id}/status`,
      { status: newStatus }
    );
    success.value = response.data.message;
    await loadExaminers();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to change status";
  }
}

onMounted(loadExaminers);
</script>
