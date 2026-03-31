<template>

<div class="container mt-4">

<h2>Review Application</h2>

<div class="card p-4">

<p><b>Student Name:</b> {{application.student}}</p>
<p><b>Status:</b> {{application.status}}</p>

<div class="mt-3">

<button
class="btn btn-success me-2"
@click="updateStatus('Shortlisted')">
Shortlist
</button>

<button
class="btn btn-danger"
@click="updateStatus('Rejected')">
Reject
</button>

<button
class="btn btn-secondary ms-2"
@click="goBack">
Back
</button>

</div>

</div>

</div>

</template>


<script>

import api from "../api/api"

export default{

data(){

return{
application:{}
}

},

mounted(){

this.loadApplication()

},

methods:{


loadApplication(){

let id = this.$route.params.id

api.get(`/company/application/${id}`)
.then(res=>{
this.application = res.data
})

},


updateStatus(status){

let id = this.$route.params.id

api.post(`/company/review/${id}`,{
status:status
})
.then(()=>{

alert("Application status updated")

this.$router.push("/company")

})

},


goBack(){

this.$router.back()

}

}

}

</script>


<style>

.card{
max-width:600px;
margin:auto;
}

</style>