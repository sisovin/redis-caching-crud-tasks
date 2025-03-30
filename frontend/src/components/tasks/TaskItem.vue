<template>
  <div>
    <h2>Task Details</h2>
    <p><strong>Title:</strong> {{ task.title }}</p>
    <p><strong>Description:</strong> {{ task.description }}</p>
    <p><strong>Completed:</strong> {{ task.completed ? 'Yes' : 'No' }}</p>
    <button @click="editTask">Edit</button>
    <button @click="deleteTask">Delete</button>
  </div>
</template>

<script>
export default {
  props: {
    task: {
      type: Object,
      required: true,
    },
  },
  methods: {
    editTask() {
      this.$emit('edit', this.task);
    },
    deleteTask() {
      this.$emit('delete', this.task.id);
    },
  },
};
</script>

<style scoped>
div {
  margin-bottom: 1rem;
}

button {
  margin-right: 0.5rem;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
}
</style>
