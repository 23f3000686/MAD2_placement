
<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold">Student Examination Booking</h2>
        <p class="text-muted">View examinations and book available slots</p>
      </div>
      <router-link to="/student/dashboard" class="btn btn-outline-secondary">
        Back to Dashboard
      </router-link>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5>Available Examinations</h5>

        <div class="table-responsive">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Examination</th>
                <th>Type</th>
                <th>Duration</th>
                <th>Status</th>
                <th>Booking</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="exam in examinations" :key="exam.id">
                <td>{{ exam.name }}</td>
                <td>{{ exam.exam_type }}</td>
                <td>{{ exam.duration }} min</td>
                <td>{{ exam.status }}</td>
                <td>
                  <span
                    class="badge"
                    :class="exam.booking_open ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ exam.booking_open ? "Open" : "Closed" }}
                  </span>
                </td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="selectExamination(exam)"
                  >
                    View Slots
                  </button>
                </td>
              </tr>

              <tr v-if="examinations.length === 0">
                <td colspan="6" class="text-center text-muted">
                  No examinations available.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="selectedExam" class="card shadow-sm mb-4">
      <div class="card-body">
        <h5>Slots for {{ selectedExam.name }}</h5>

        <div v-if="loadingSlots" class="text-muted">Loading slots...</div>

        <div v-else class="table-responsive">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Slot ID</th>
                <th>Start (IST)</th>
                <th>End (IST)</th>
                <th>Capacity</th>
                <th>Available Seats</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="slot in slots" :key="slot.id">
                <td>{{ slot.id }}</td>
                <td>{{ formatDate(slot.start_time) }}</td>
                <td>{{ formatDate(slot.end_time) }}</td>
                <td>{{ slot.capacity }}</td>
                <td>{{ slot.available_seats }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-success"
                    :disabled="bookingId === slot.id || !slot.booking_open || slot.available_seats <= 0"
                    @click="bookSlot(slot)"
                  >
                    {{ bookingId === slot.id ? "Booking..." : "Book Slot" }}
                  </button>
                </td>
              </tr>

              <tr v-if="slots.length === 0">
                <td colspan="6" class="text-center text-muted">
                  No available slots for this examination.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-body">
        <h5>My Bookings</h5>

        <div class="table-responsive">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Booking ID</th>
                <th>Examination</th>
                <th>Slot</th>
                <th>Start (IST)</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="booking in bookings" :key="booking.id">
                <td>{{ booking.id }}</td>
                <td>{{ booking.examination_name }}</td>
                <td>{{ booking.slot_id }}</td>
                <td>{{ formatDate(booking.start_time) }}</td>
                <td>{{ booking.status }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-outline-danger"
                    :disabled="booking.status.toLowerCase() !== 'booked'"
                    @click="cancelBooking(booking)"
                  >
                    Cancel
                  </button>
                </td>
              </tr>

              <tr v-if="bookings.length === 0">
                <td colspan="6" class="text-center text-muted">
                  No bookings found.
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
const bookings = ref([]);
const selectedExam = ref(null);

const error = ref("");
const success = ref("");
const loadingSlots = ref(false);
const bookingId = ref(null);

function showError(err) {
  error.value = err.response?.data?.message || err.message || "Request failed";
  success.value = "";
}

function formatDate(value) {
  return value ? value.replace("T", " ").slice(0, 16) : "-";
}

async function loadExaminations() {
  try {
    const response = await api.get("/student/examinations");
    examinations.value = response.data.examinations || [];
  } catch (err) {
    showError(err);
  }
}

async function loadBookings() {
  try {
    const response = await api.get("/student/bookings");
    bookings.value = response.data.bookings || [];
  } catch (err) {
    showError(err);
  }
}

async function selectExamination(exam) {
  selectedExam.value = exam;
  slots.value = [];
  loadingSlots.value = true;
  error.value = "";

  try {
    const response = await api.get(
      `/student/examinations/${exam.id}/slots`
    );
    slots.value = response.data.slots || [];
  } catch (err) {
    showError(err);
  } finally {
    loadingSlots.value = false;
  }
}

async function bookSlot(slot) {
  if (!confirm(`Book slot #${slot.id}?`)) return;

  error.value = "";
  success.value = "";
  bookingId.value = slot.id;

  try {
    const response = await api.post("/student/bookings", {
      slot_id: slot.id,
    });

    success.value = response.data.message || "Slot booked successfully";

    await loadBookings();
    if (selectedExam.value) {
      await selectExamination(selectedExam.value);
    }
  } catch (err) {
    showError(err);
  } finally {
    bookingId.value = null;
  }
}

async function cancelBooking(booking) {
  if (!confirm(`Cancel booking #${booking.id}?`)) return;

  error.value = "";
  success.value = "";

  try {
    const response = await api.patch(
      `/student/bookings/${booking.id}/cancel`
    );

    success.value = response.data.message || "Booking cancelled successfully";

    await loadBookings();
    if (selectedExam.value) {
      await selectExamination(selectedExam.value);
    }
  } catch (err) {
    showError(err);
  }
}

onMounted(async () => {
  await Promise.all([loadExaminations(), loadBookings()]);
});
</script>
