<template>

<div class="container mt-5">

<h2 class="mb-3">Register</h2>

<div class="card p-4">

<!-- Role Selection -->

<label class="mb-1">Register As</label>

<select class="form-control mb-3" v-model="role">

<option value="student">Student</option>
<option value="company">Company</option>

</select>


<!-- Common Fields -->

<input
class="form-control mb-2"
placeholder="Name"
v-model="name"
/>

<input
class="form-control mb-2"
placeholder="Email"
v-model="email"
/>

<input
type="password"
class="form-control mb-2"
placeholder="Password"
v-model="password"
/>


<!-- Student Fields -->

<div v-if="role === 'student'">

<input
class="form-control mb-2"
placeholder="Branch"
v-model="branch"
/>

<input
class="form-control mb-2"
placeholder="CGPA"
v-model="cgpa"
/>

<input
class="form-control mb-2"
placeholder="Year"
v-model="year"
/>

</div>


<!-- Company Fields -->

<div v-if="role === 'company'">

<input
class="form-control mb-2"
placeholder="Company Name"
v-model="company_name"
/>

</div>


<button
class="btn btn-success w-100 mt-2"
@click="register"
>
Register
</button>


<p class="mt-3"
:class="message.includes('Failed') ? 'text-danger' : 'text-success'">

{{message}}

</p>

</div>

</div>

</template>


<script>

import api from "../api/api"

export default {

data(){

return{

role:"student",

name:"",
email:"",
password:"",

branch:"",
cgpa:"",
year:"",

company_name:"",

message:""

}

},

methods:{


register(){

if(this.role === "student"){

api.post("/register/student",{

name:this.name,
email:this.email,
password:this.password,
branch:this.branch,
cgpa:this.cgpa,
year:this.year

})
.then(()=>{

this.message="Student Registered Successfully"

setTimeout(()=>{

this.$router.push("/")

},1500)

})
.catch(err=>{

console.log(err.response)

this.message="Registration Failed"

})

}


if(this.role === "company"){

api.post("/register/company",{

name:this.name,
email:this.email,
password:this.password,
company_name:this.company_name

})
.then(()=>{

this.message="Company Registered (Waiting for Admin Approval)"

setTimeout(()=>{

this.$router.push("/")

},1500)

})
.catch(err=>{

console.log(err.response)

this.message="Registration Failed"

})

}

}

}

}

</script>


<style>

.card{

max-width:500px;
margin:auto;

}

</style>