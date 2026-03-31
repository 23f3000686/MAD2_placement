<template>

<div class="container mt-4">

<!-- Header -->

<div class="d-flex justify-content-between align-items-center mb-3">

<h3>Welcome Organization</h3>

<button class="btn btn-danger btn-sm" @click="logout">
Logout
</button>

</div>


<!-- Create Drive Button -->

<div class="text-end mb-3">

<button class="btn btn-success" @click="showForm = !showForm">
Create Drive
</button>

</div>


<!-- Create Drive Form -->

<div v-if="showForm" class="card p-3 mb-4">

<h5>Create Placement Drive</h5>

<input
class="form-control mb-2"
placeholder="Job Title"
v-model="job_title"
/>

<textarea
class="form-control mb-2"
placeholder="Description"
v-model="description">
</textarea>

<input
class="form-control mb-2"
placeholder="Eligibility CGPA"
v-model="eligibility_cgpa"
/>

<input
class="form-control mb-2"
placeholder="Application Deadline"
v-model="deadline"
/>

<button
class="btn btn-primary"
@click="createDrive">
Create Drive
</button>

</div>


<!-- Upcoming Drives -->

<div class="card p-3 mb-4">

<h5>Upcoming Drives</h5>

<table class="table">

<tr>
<th>Sr No</th>
<th>Drive Name</th>
<th>Actions</th>
</tr>

<tr v-for="(d,index) in upcomingDrives" :key="d.id">

<td>{{index+1}}</td>
<td>{{d.job_title}}</td>

<td>

<button
class="btn btn-outline-primary btn-sm me-2"
@click="viewApplicants(d.id)">
View Details
</button>

<button
class="btn btn-success btn-sm"
@click="completeDrive(d.id)">
Mark as Complete
</button>

</td>

</tr>

</table>

</div>


<!-- Closed Drives -->

<div class="card p-3">

<h5>Closed Drives</h5>

<table class="table">

<tr>
<th>Sr No</th>
<th>Drive Name</th>
<th>Actions</th>
</tr>

<tr v-for="(d,index) in closedDrives" :key="d.id">

<td>{{index+1}}</td>
<td>{{d.job_title}}</td>

<td>

<button
class="btn btn-primary btn-sm"
@click="updateDrive(d.id)">
Update
</button>

</td>

</tr>

</table>

</div>

</div>

</template>



<script>

import api from "../api/api"

export default {

data(){

return{

showForm:false,

job_title:"",
description:"",
eligibility_cgpa:"",
deadline:"",

drives:[]

}

},

mounted(){

this.loadDrives()

},

computed:{

upcomingDrives(){
return this.drives.filter(d => d.status !== "completed")
},

closedDrives(){
return this.drives.filter(d => d.status === "completed")
}

},

methods:{


loadDrives(){

api.get("/company/drives")
.then(res=>{
this.drives = res.data
})

},


createDrive(){

api.post("/company/create-drive",{

company_id:1,
job_title:this.job_title,
description:this.description,
eligibility_cgpa:this.eligibility_cgpa,
deadline:this.deadline

}).then(()=>{

this.loadDrives()
this.showForm=false

})

},


viewApplicants(id){

this.$router.push(`/drive-applicants/${id}`)

},


completeDrive(id){

api.post(`/company/drive/complete/${id}`)
.then(()=>{

this.loadDrives()

})

},


updateDrive(id){

alert("Update Drive Feature")

},


logout(){

localStorage.clear()
this.$router.push("/")

}

}

}

</script>