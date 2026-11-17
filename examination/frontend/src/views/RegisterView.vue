
<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-7 col-lg-5">
        <div class="card border-0 shadow-sm rounded-4">
          <div class="card-body p-4">
            <div class="text-center mb-4">
              <i class="bi bi-person-plus fs-1 text-primary"></i>
              <h3 class="fw-bold mt-2">Student Registration</h3>
              <p class="text-muted">
                Create your Examination Management Portal account
              </p>
            </div>

            <div v-if="error" class="alert alert-danger">
              {{ error }}
            </div>

            <div v-if="success" class="alert alert-success">
              {{ success }}
            </div>

            <form @submit.prevent="registerStudent">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input
                  v-model.trim="form.name"
                  type="text"
                  class="form-control"
                  maxlength="100"
                  required
                  placeholder="Enter your full name"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Email Address</label>
                <input
                  v-model.trim="form.email"
                  type="email"
                  class="form-control"
                  maxlength="120"
                  required
                  placeholder="Enter your email"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Contact Number (Optional)</label>
                <input
                  v-model.trim="form.contact"
                  type="tel"
                  class="form-control"
                  maxlength="20"
                  placeholder="Enter contact number"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  minlength="8"
                  required
                  placeholder="Minimum 8 characters"
                />
              </div>

              <div class="mb-4">
                <label class="form-label">Confirm Password</label>
                <input
                  v-model="confirmPassword"
                  type="password"
                  class="form-control"
                  required
                  placeholder="Re-enter your password"
                />
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                <span
                  v-if="loading"
                  class="spinner-border spinner-border-sm me-2"
                ></span>
                {{ loading ? "Registering..." : "Register" }}
              </button>
            </form>

            <p class="text-center mt-4 mb-0">
              Already have an account?
              <router-link to="/login">Login here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api.js";

const router = useRouter();

const form = ref({
  name: "",
  email: "",
  contact: "",
  password: "",
});

const confirmPassword = ref("");
const error = ref("");
const success = ref("");
const loading = ref(false);

async function registerStudent() {
  error.value = "";
  success.value = "";

  if (form.value.password !== confirmPassword.value) {
    error.value = "Passwords do not match";
    return;
  }

  if (form.value.password.length < 8) {
    error.value = "Password must contain at least 8 characters";
    return;
  }

  loading.value = true;

  try {
    const response = await api.post("/auth/register", {
      name: form.value.name,
      email: form.value.email,
      contact: form.value.contact,
      password: form.value.password,
    });

    success.value = response.data.message;

    form.value = {
      name: "",
      email: "",
      contact: "",
      password: "",
    };
    confirmPassword.value = "";

    // Registration does not log the student in automatically.
    // Send them to the login page after successful registration.
    await router.push("/login");
  } catch (err) {
    error.value =
      err.response?.data?.message || "Registration failed. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>
