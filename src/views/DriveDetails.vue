<template>

<div class="container mt-4">

<div class="card p-4">

<h3>{{drive.job_title}}</h3>

<p><b>Description:</b> {{drive.description}}</p>

<p><b>Eligibility CGPA:</b> {{drive.eligibility_cgpa}}</p>

<p><b>Deadline:</b> {{drive.deadline}}</p>

<button
class="btn btn-success me-2"
@click="applyDrive">
Apply
</button>

<button
class="btn btn-secondary" @click="$router.push('/student')">
Go Back
</button>

</div>

</div>

</template>


<script>

import api from "../api/api"

export default{

data(){

return{

drive:{}

}

},

mounted(){

this.loadDrive()

},

methods:{

loadDrive(){

let id = this.$route.params.id

api.get(`/student/drive/${id}`)

.then(res=>{
this.drive = res.data
})

},

applyDrive(){

api.post(`/student/apply/${this.$route.params.id}`)

.then(()=>{
alert("Applied Successfully")
})

}

}
}

</script>