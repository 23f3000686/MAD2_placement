
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Course Management</h2>
        <p class="text-muted">Manage examination courses</p>
      </div>
      <router-link to="/admin/dashboard" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-2"></i>Dashboard
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-6">
            <label class="form-label">Search courses</label>
            <input
              v-model="search"
              class="form-control"
              placeholder="Search by course code or name"
              @keyup.enter="loadCourses"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select v-model="statusFilter" class="form-select" @change="loadCourses">
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="col-md-3 d-flex gap-2">
            <button class="btn btn-primary" @click="loadCourses">
              Search
            </button>
            <button class="btn btn-success" @click="openAdd">
              <i class="bi bi-plus-lg me-1"></i>Add Course
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white">
        <h5 class="mb-0">{{ editingId ? "Edit Course" : "Add Course" }}</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="saveCourse">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Course Code *</label>
              <input
                v-model.trim="form.code"
                class="form-control"
                maxlength="20"
                required
              />
            </div>
            <div class="col-md-8">
              <label class="form-label">Course Name *</label>
              <input
                v-model.trim="form.name"
                class="form-control"
                maxlength="100"
                required
              />
            </div>
            <div class="col-md-8">
              <label class="form-label">Description</label>
              <textarea v-model="form.description" class="form-control" rows="3"></textarea>
            </div>
            <div class="col-md-4">
              <label class="form-label">Status</label>
              <select v-model="form.status" class="form-select">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div class="mt-3 d-flex gap-2">
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "Saving..." : editingId ? "Update Course" : "Create Course" }}
            </button>
            <button type="button" class="btn btn-secondary" @click="showForm = false">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="mb-3">Courses ({{ courses.length }})</h5>

        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Code</th>
                <th>Name</th>
                <th>Description</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="course in courses" :key="course.id">
                <td>{{ course.id }}</td>
                <td><strong>{{ course.code }}</strong></td>
                <td>{{ course.name }}</td>
                <td>{{ course.description || "—" }}</td>
                <td>
                  <span
                    class="badge"
                    :class="course.status === 'active' ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ course.status }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-outline-primary" @click="openEdit(course)">
                      Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" @click="deleteCourse(course)">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="courses.length === 0">
                <td colspan="6" class="text-center text-muted py-4">
                  No courses found
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

const courses = ref([]);
const search = ref("");
const statusFilter = ref("");
const loading = ref(false);
const saving = ref(false);
const showForm = ref(false);
const editingId = ref(null);
const error = ref("");
const success = ref("");

const emptyForm = () => ({
  code: "",
  name: "",
  description: "",
  status: "active",
});

const form = ref(emptyForm());

async function loadCourses() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/admin/courses", {
      params: {
        search: search.value,
        status: statusFilter.value,
      },
    });
    courses.value = response.data.courses || [];
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load courses";
  } finally {
    loading.value = false;
  }
}

function openAdd() {
  editingId.value = null;
  form.value = emptyForm();
  showForm.value = true;
  error.value = "";
  success.value = "";
}

function openEdit(course) {
  editingId.value = course.id;
  form.value = {
    code: course.code,
    name: course.name,
    description: course.description || "",
    status: course.status,
  };
  showForm.value = true;
  error.value = "";
  success.value = "";
}

async function saveCourse() {
  saving.value = true;
  error.value = "";
  success.value = "";

  try {
    const payload = {
      ...form.value,
      code: form.value.code.trim().toUpperCase(),
    };

    if (editingId.value !== null) {
      await api.put(`/admin/courses/${editingId.value}`, payload);
      success.value = "Course updated successfully";
    } else {
      await api.post("/admin/courses", payload);
      success.value = "Course created successfully";
    }

    showForm.value = false;
    await loadCourses();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to save course";
  } finally {
    saving.value = false;
  }
}

async function deleteCourse(course) {
  if (!window.confirm(`Delete course ${course.code}?`)) return;

  error.value = "";
  success.value = "";

  try {
    await api.delete(`/admin/courses/${course.id}`);
    success.value = "Course deleted successfully";
    await loadCourses();
  } catch (err) {
    error.value = err.response?.data?.message || "Cannot delete course";
  }
}

onMounted(loadCourses);
</script>
