<template>

<div class="container mt-4">

<h2>Apply for Drive</h2>

<button
class="btn btn-success"
@click="submitApplication">
Submit Application
</button>

<p v-if="message" class="mt-3 text-success">
{{message}}
</p>

</div>

</template>

<script>

import api from "../api/api"

export default{

data(){
return{
message:""
}
},

methods:{

submitApplication(){

let driveId = this.$route.params.id

api.post(`/student/apply/${driveId}`)
.then(()=>{
this.message = "Application Submitted Successfully"
})
.catch(()=>{
this.message = "Application Failed"
})

}

}

}

</script>