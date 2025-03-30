<template>
  <div id="app">
    <nav>
      <router-link to="/tasks">Tasks</router-link>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
nav {
  margin-bottom: 1rem;
}
</style>
