import Vue from "vue"
import Router from "vue-router"

import Login from "../views/Login.vue"
import AdminDashboard from "../views/AdminDashboard.vue"
import StudentDashboard from "../views/StudentDashboard.vue"
import CompanyDashboard from "../views/CompanyDashboard.vue"
import Register from "../views/Register.vue"
import DriveDetails from "../views/DriveDetails.vue"
import StudentApplication from "../views/StudentApplication.vue"
import ApplicationHistory from "../views/ApplicationHistory.vue"
import DriveApplicants from "../views/DriveApplicants.vue"
import ReviewApplication from "../views/ReviewApplication.vue"

Vue.use(Router)

export default new Router({

routes: [

{ path: "/", component: Login },

{ path: "/register", component: Register },

{ path: "/admin", component: AdminDashboard },
{ path: "/student", component: StudentDashboard },
{ path: "/company", component: CompanyDashboard },
{ path: "/drive-applicants/:id", component: DriveApplicants},
{ path: "/drive/:id", component: DriveDetails },
{ path: "/apply/:id", component: StudentApplication },
{ path: "/history", component: ApplicationHistory },
{ path: "/application/:id",component: ReviewApplication}
]

})