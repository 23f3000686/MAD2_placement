<template>

<div class="container mt-4">

<h3>Drive Applications</h3>

<div class="card p-3">

<table class="table">

<tr>
<th>Student</th>
<th>Status</th>
<th>Action</th>
</tr>

<tr v-for="a in applications" :key="a.application_id">

<td>{{a.student}}</td>
<td>{{a.status}}</td>

<td>

<button
class="btn btn-primary btn-sm"
@click="review(a.id)">
Review Application
</button>

</td>

</tr>

</table>

</div>

</div>

</template>

<script>

import api from "../api/api"

export default{

data(){
return{
applications:[]
}
},

mounted(){
this.loadApplications()
},

methods:{

loadApplications(){

let id = this.$route.params.id

api.get(`/company/applications/${id}`)

.then(res=>{
this.applications = res.data
})

},

review(id){
this.$router.push(`/application/${id}`)
}

}

}

</script>