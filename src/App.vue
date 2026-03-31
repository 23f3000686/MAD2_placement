<template>
  <div id="app">

    <nav class="navbar navbar-dark bg-dark">
      <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">
          Placement Portal
        </span>
      </div>
    </nav>

    <div class="container mt-5">
      <router-view />
    </div>

  </div>
</template>

<script>
export default {
  name: "App"
}
</script>

<style>

body{
  margin:0;
  background:#f5f7fa;
  font-family: Arial, Helvetica, sans-serif;
}

/* Navbar */
.navbar{
  padding:15px;
  font-size:20px;
  font-weight:bold;
}

/* Page container */
.container{
  background:white;
  padding:30px;
  border-radius:10px;
  box-shadow:0 4px 10px rgba(0,0,0,0.1);
}

</style>