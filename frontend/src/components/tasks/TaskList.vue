<template>
  <div>
    <h2>Task List</h2>
    <table>
      <thead>
        <tr>
          <th>Title</th>
          <th>Description</th>
          <th>Completed</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id">
          <td>{{ task.title }}</td>
          <td>{{ task.description }}</td>
          <td>{{ task.completed ? 'Yes' : 'No' }}</td>
          <td>
            <button @click="completeTask(task.id)">Complete</button>
            <button @click="deleteTask(task.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  computed: {
    ...mapState('tasks', ['tasks']),
  },
  methods: {
    ...mapActions('tasks', ['fetchTasks', 'deleteTask', 'completeTask']),
  },
  created() {
    this.fetchTasks();
  },
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.5rem;
  border: 1px solid #ddd;
  text-align: left;
}

th {
  background-color: #f4f4f4;
}

button {
  margin-right: 0.5rem;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
}
</style>
