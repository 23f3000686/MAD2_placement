<template>

<div class="container mt-5">

<h2>Login</h2>

<input class="form-control" placeholder="Email" v-model="email">

<br>

<input class="form-control"
type="password"
placeholder="Password"
v-model="password">

<br>

<button class="btn btn-primary" @click="login">
Login
</button>

<p class="text-danger">{{message}}</p>

<hr>

<p>
New User? 
<router-link to="/register">
Register
</router-link>
</p>

</div>

</template>

<script>

import api from "../api/api"

export default {

data(){

return{

email:"",
password:"",
message:""

}

},

methods:{

login(){

api.post("/login",{

email:this.email,
password:this.password

})
.then(res=>{

let role=res.data.role

if(role==="admin") this.$router.push("/admin")

if(role==="student") this.$router.push("/student")

if(role==="company") this.$router.push("/company")

})
.catch(()=>{

this.message="Invalid Login"

})

}

}

}

</script>

<style>

.container{
max-width:400px;
}

</style>