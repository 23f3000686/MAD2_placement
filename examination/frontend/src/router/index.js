import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import AdminDashboard from "../views/AdminDashboard.vue";
import ExaminerDashboard from "../views/ExaminerDashboard.vue";
import StudentDashboard from "../views/StudentDashboard.vue";
import AdminCourses from "../views/AdminCourses.vue";
import AdminExaminations from "../views/AdminExaminations.vue";
import AdminRubrics from "../views/AdminRubrics.vue";
import AdminExaminers from "../views/AdminExaminers.vue";
import AdminAssignments from "../views/AdminAssignments.vue";
import ExaminerSlots from "../views/ExaminerSlots.vue";
import ExaminerEvaluations from "../views/ExaminerEvaluations.vue";
import StudentBookings from "../views/StudentBookings.vue";
import StudentResults from "../views/StudentResults.vue";
import AdminResults from "../views/AdminResults.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },

  {
    path: "/admin/dashboard",
    component: AdminDashboard,
    meta: { role: "admin" },
  },
  {
    path: "/examiner/dashboard",
    component: ExaminerDashboard,
    meta: { role: "examiner" },
  },
  {
    path: "/student/dashboard",
    component: StudentDashboard,
    meta: { role: "student" },
  },
  {
    path: "/admin/courses",
    component: AdminCourses,
    meta: { role: "admin" },
  },
  {
  path: "/register",
  component: RegisterView,
  },
  {
  path: "/admin/examinations",
  component: AdminExaminations,
  meta: { role: "admin" },
  },
  {
  path: "/admin/rubrics",
  component: AdminRubrics,
  meta: { role: "admin" },
  },
  {
  path: "/admin/examiners",
  component: AdminExaminers,
    meta: { role: "admin" },
  },
  {
  path: "/admin/assignments",
  component: AdminAssignments,
  meta: { role: "admin" },
  },
  {
  path: "/examiner/slots",
  component: ExaminerSlots,
  meta: { role: "examiner" },
  },
  {
  path: "/examiner/evaluations",
  component: ExaminerEvaluations,
  meta: { role: "examiner" },
  },
  {
  path: "/student/bookings",
  component: StudentBookings,
  meta: { role: "student" },
  },
  {
  path: "/student/results",
  component: StudentResults,
  meta: { role: "student" },
  },
  {
  path: "/admin/results",
  component: AdminResults,
  meta: { role: "admin" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (!to.meta.role) return true;

  const user = JSON.parse(sessionStorage.getItem("user") || "null");

  if (!user) return "/login";

  if (user.role !== to.meta.role) {
    return `/${user.role}/dashboard`;
  }

  return true;
});

export default router;