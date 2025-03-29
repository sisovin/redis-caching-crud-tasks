<template>
  <div id="app">
    <TaskForm @add-task="addTask" />
    <TaskList :tasks="tasks" @delete-task="deleteTask" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import TaskForm from './components/TaskForm.vue';
import TaskList from './components/TaskList.vue';

export default defineComponent({
  name: 'App',
  components: {
    TaskForm,
    TaskList,
  },
  setup() {
    const tasks = ref([]);

    const addTask = (task: { title: string; description: string }) => {
      tasks.value.push(task);
    };

    const deleteTask = (index: number) => {
      tasks.value.splice(index, 1);
    };

    return {
      tasks,
      addTask,
      deleteTask,
    };
  },
});
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
