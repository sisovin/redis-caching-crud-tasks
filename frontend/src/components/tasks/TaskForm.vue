<template>
  <div>
    <h2>{{ isEditMode ? 'Edit Task' : 'Create Task' }}</h2>
    <form @submit.prevent="handleSubmit">
      <div>
        <label for="title">Title</label>
        <input type="text" v-model="task.title" id="title" required />
      </div>
      <div>
        <label for="description">Description</label>
        <textarea v-model="task.description" id="description" required></textarea>
      </div>
      <div>
        <label for="completed">Completed</label>
        <input type="checkbox" v-model="task.completed" id="completed" />
      </div>
      <button type="submit">{{ isEditMode ? 'Update Task' : 'Create Task' }}</button>
    </form>
  </div>
</template>

<script>
export default {
  props: {
    task: {
      type: Object,
      default: () => ({
        title: '',
        description: '',
        completed: false,
      }),
    },
    isEditMode: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    handleSubmit() {
      if (this.validateForm()) {
        this.$emit('submit', this.task);
      }
    },
    validateForm() {
      if (!this.task.title || !this.task.description) {
        alert('Please fill in all required fields.');
        return false;
      }
      return true;
    },
  },
};
</script>

<style scoped>
form {
  display: flex;
  flex-direction: column;
}

div {
  margin-bottom: 1rem;
}

label {
  margin-bottom: 0.5rem;
}

input,
textarea {
  padding: 0.5rem;
  font-size: 1rem;
}

button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
}
</style>
