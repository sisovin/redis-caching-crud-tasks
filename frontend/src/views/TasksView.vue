<template>
  <div>
    <h1>Tasks</h1>
    <TaskForm @submit="handleTaskSubmit" />
    <TaskList @edit="handleTaskEdit" @delete="handleTaskDelete" />
  </div>
</template>

<script>
import TaskForm from '../components/tasks/TaskForm.vue';
import TaskList from '../components/tasks/TaskList.vue';
import { mapActions } from 'vuex';

export default {
  components: {
    TaskForm,
    TaskList,
  },
  methods: {
    ...mapActions('tasks', ['createTask', 'updateTask', 'deleteTask']),
    handleTaskSubmit(task) {
      if (task.id) {
        this.updateTask(task);
      } else {
        this.createTask(task);
      }
    },
    handleTaskEdit(task) {
      this.$refs.taskForm.task = task;
      this.$refs.taskForm.isEditMode = true;
    },
    handleTaskDelete(taskId) {
      this.deleteTask(taskId);
    },
  },
};
</script>

<style scoped>
h1 {
  margin-bottom: 1rem;
}
</style>
