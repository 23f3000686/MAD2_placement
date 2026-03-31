<template>

<div class="dashboard">

<div class="sidebar">

<h4>Placement Portal</h4>

<ul>

<li><router-link to="/admin">Admin</router-link></li>
<li><router-link to="/student">Student</router-link></li>
<li><router-link to="/company">Company</router-link></li>

</ul>

</div>

<div class="content">

<slot></slot>

</div>

</div>

</template>

<style>

.dashboard{
display:flex;
height:100vh;
}

.sidebar{
width:220px;
background:#1e293b;
color:white;
padding:20px;
}

.sidebar ul{
list-style:none;
padding:0;
}

.sidebar li{
margin:10px 0;
}

.sidebar a{
color:white;
text-decoration:none;
}

.content{
flex:1;
padding:30px;
background:#f1f5f9;
}

</style>