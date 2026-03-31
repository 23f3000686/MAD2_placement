<template>

<div class="container mt-4">

<!-- Header -->

<div class="d-flex justify-content-between align-items-center mb-3">

<h4>Students' Dashboard</h4>

<div>

<button class="btn btn-sm btn-secondary me-2" @click="$router.push('/history')">
History
</button>

<button class="btn btn-sm btn-danger" @click="logout">
Logout
</button>

</div>

</div>

<div class="card p-3 mb-4">

<h5>Welcome {{studentName}}</h5>

</div>


<!-- Organizations -->

<div class="card p-3 mb-4">

<h5>Organizations</h5>

<div
class="d-flex justify-content-between align-items-center border p-2 mb-2"
v-for="c in companies"
:key="c.id"
>

<span>{{c.name}}</span>

<button
class="btn btn-primary btn-sm"
@click="viewCompany(c.id)"
>
View Details
</button>

</div>

</div>


<!-- Applied Drives -->

<div class="card p-3">

<h5>Applied Drives</h5>

<table class="table">

<tr>
<th>Sr No.</th>
<th>Drive Name</th>
<th>Company</th>
<th>Date</th>
<th></th>
</tr>

<tr v-for="(d,index) in drives" :key="d.id">

<td>{{index+1}}</td>

<td>{{d.title}}</td>

<td>{{d.company}}</td>

<td>{{d.date}}</td>

<td>

<button
class="btn btn-primary btn-sm"
@click="viewDrive(d.id)"
>
View Details
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

studentName:"Student",

companies:[],

drives:[]

}

},

mounted(){

this.loadCompanies()
this.loadApplications()

},

methods:{


loadCompanies(){

api.get("/student/companies")

.then(res=>{

this.companies = res.data

})

},


loadApplications(){

api.get("/student/applications")

.then(res=>{

this.drives = res.data

})

},


viewCompany(id){

this.$router.push(`/drive/${id}`)

},


viewDrive(id){

this.$router.push(`/drive/${id}`)

},


logout(){

localStorage.clear()
this.$router.push("/")

}

}

}

</script>