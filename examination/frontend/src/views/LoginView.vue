<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100">
    <div class="card shadow border-0 p-4" style="width: 100%; max-width: 430px;">
      <div class="card-body">
        <h3 class="text-center fw-bold mb-2">Examination Management Portal</h3>
        <p class="text-center text-muted mb-4">Sign in to your account</p>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <form @submit.prevent="login">
          <div class="mb-3">
            <label class="form-label">Email Address</label>
            <input v-model.trim="email" type="email" class="form-control" required placeholder="Enter your email" />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required placeholder="Enter your password" />
          </div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? "Signing in..." : "Login" }}
          </button>
        </form>

        <p class="text-center mt-4 mb-0">
          New student?
          <router-link to="/register">Create an account</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api.js";

const router = useRouter();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function login() {
  error.value = "";
  loading.value = true;

  try {
    const response = await api.post("/auth/login", {
      email: email.value,
      password: password.value,
    });

    const user = response.data.user;

    if (!user || !["admin", "examiner", "student"].includes(user.role)) {
      throw new Error("Unexpected login response. Check the backend user data.");
    }

    sessionStorage.setItem("user", JSON.stringify(user));

    if (user.role === "admin") {
      await router.push("/admin/dashboard");
    } else if (user.role === "examiner") {
      await router.push("/examiner/dashboard");
    } else {
      await router.push("/student/dashboard");
    }
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      err.message ||
      "Login failed. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>