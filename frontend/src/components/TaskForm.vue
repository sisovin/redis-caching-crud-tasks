<template>
  <form @submit.prevent="onSubmit">
    <div>
      <label for="title">Title:</label>
      <input type="text" id="title" v-model="title" required />
    </div>
    <div>
      <label for="description">Description:</label>
      <textarea id="description" v-model="description" required></textarea>
    </div>
    <button type="submit">Add Task</button>
  </form>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'TaskForm',
  emits: ['add-task'],
  setup(_, { emit }) {
    const title = ref('');
    const description = ref('');

    const onSubmit = () => {
      if (title.value && description.value) {
        emit('add-task', { title: title.value, description: description.value });
        title.value = '';
        description.value = '';
      }
    };

    return {
      title,
      description,
      onSubmit,
    };
  },
});
</script>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  font-weight: bold;
}

button {
  align-self: flex-start;
}
</style>
