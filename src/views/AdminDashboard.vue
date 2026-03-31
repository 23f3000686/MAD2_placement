<template>

<div class="container mt-4">
<div class="d-flex align-items-center mb-4 w-100">

<h3 class="mb-0">Admin Dashboard</h3>

<button class="btn btn-danger ms-auto" @click="logout">
Logout
</button>

</div>
<!-- Stats -->

<div class="row mb-4">

<div class="col-md-4">
<div class="card p-3 text-center">
<h5>Total Students</h5>
<h3>{{stats.students}}</h3>
</div>
</div>

<div class="col-md-4">
<div class="card p-3 text-center">
<h5>Total Companies</h5>
<h3>{{stats.companies}}</h3>
</div>
</div>

<div class="col-md-4">
<div class="card p-3 text-center">
<h5>Total Drives</h5>
<h3>{{stats.drives}}</h3>
</div>
</div>

</div>

<!-- Company Registrations -->

<div class="card p-3 mb-4">

<h5 class="mb-3">Company Registrations</h5>

<table class="table table-bordered">

<thead>
<tr>
<th>Name</th>
<th>Status</th>
<th>Action</th>
</tr>
</thead>

<tbody>

<tr v-for="c in companies" :key="c.id">

<td>{{c.name}}</td>

<td>
<span v-if="c.status" class="text-success">Approved</span>
<span v-else class="text-warning">Pending</span>
</td>

<td>

<button
v-if="!c.status"
class="btn btn-success btn-sm"
@click="approveCompany(c.id)">
Approve
</button>

<span v-else class="text-muted">Already Approved</span>

</td>

</tr>

</tbody>

</table>

</div>

<!-- Ongoing Drives -->

<div class="card p-3 mb-4">

<h5 class="mb-3">Ongoing Drives</h5>

<table class="table table-bordered">

<thead>
<tr>
<th>Sr No</th>
<th>Drive Name</th>
<th>Actions</th>
</tr>
</thead>

<tbody>

<tr v-for="(d,index) in ongoingDrives" :key="d.id">

<td>{{index+1}}</td>
<td>{{d.name}}</td>

<td>

<button
class="btn btn-primary btn-sm me-2"
@click="viewDrive(d.id)">
View Details
</button>

<button
class="btn btn-success btn-sm"
@click="completeDrive(d.id)">
Mark as Complete
</button>

</td>

</tr>

</tbody>

</table>

</div>

<!-- Closed Drives -->

<div class="card p-3 mb-4">

<h5 class="mb-3">Closed Drives</h5>

<table class="table table-bordered">

<thead>
<tr>
<th>Sr No</th>
<th>Drive Name</th>
</tr>
</thead>

<tbody>

<tr v-for="(d,index) in closedDrives" :key="d.id">

<td>{{index+1}}</td>
<td>{{d.name}}</td>

</tr>

</tbody>

</table>

</div>

<!-- Student Applications -->

<div class="card p-3">

<h5 class="mb-3">Student Applications</h5>

<table class="table table-bordered">

<thead>
<tr>
<th>Sr No</th>
<th>Name</th>
<th>Drive</th>
<th>Company</th>
<th>Action</th>
</tr>
</thead>

<tbody>

<tr v-for="(a,index) in applications" :key="a.id">

<td>{{index+1}}</td>
<td>{{a.student}}</td>
<td>{{a.drive}}</td>
<td>{{a.company}}</td>

<td>

<button
class="btn btn-outline-primary btn-sm"
@click="viewApplication(a.id)">
View
</button>

</td>

</tr>

</tbody>

</table>

</div>

</div>

</template>

<script>

import api from "../api/api"

export default {

data(){

return{

stats:{
students:0,
companies:0,
drives:0
},

companies:[],
ongoingDrives:[],
closedDrives:[],
applications:[]

}

},

mounted(){

this.loadStats()
this.loadCompanies()
this.loadDrives()
this.loadApplications()

},

methods:{


loadStats(){

api.get("/admin/stats")
.then(res=>{
this.stats = res.data
})

},


loadCompanies(){

api.get("/admin/companies")
.then(res=>{
this.companies = res.data
})

},


loadDrives(){

api.get("/admin/drives")
.then(res=>{

this.ongoingDrives = res.data.filter(d => d.status !== "completed")

this.closedDrives = res.data.filter(d => d.status === "completed")

})

},


loadApplications(){

api.get("/admin/applications")
.then(res=>{
this.applications = res.data
})

},


approveCompany(id){

api.post(`/admin/company/approve/${id}`)
.then(()=>{
this.loadCompanies()
this.loadStats()
})

},


completeDrive(id){

api.post(`/admin/drive/complete/${id}`)
.then(()=>{
this.loadDrives()
})

},


viewDrive(id){

this.$router.push(`/drive/${id}`)

},

logout(){

localStorage.removeItem("token")
localStorage.removeItem("user")

this.$router.push("/")

},

viewApplication(id){

this.$router.push(`/application/${id}`)

}

}

}

</script>