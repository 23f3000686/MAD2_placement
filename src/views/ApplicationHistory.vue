<template>

<div class="container">
<div class="d-flex justify-content-between align-items-center mb-3">
<h2>Application History</h2>
<div>
<button class="btn btn-sm btn-secondary me-2" @click="$router.push('/student')">
Back
</button>
</div>
</div>
<div>
<table class="table">

<tr>

<th>Company</th>
<th>Drive</th>
<th>Status</th>

</tr>

<tr v-for="a in applications">

<td>{{a.company}}</td>
<td>{{a.drive}}</td>
<td>{{a.status}}</td>

</tr>

</table>

</div>
</div>
</template>