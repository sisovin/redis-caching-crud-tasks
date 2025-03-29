<template>
  <div class="task-item">
    <h3>{{ task.title }}</h3>
    <p>{{ task.description }}</p>
    <button @click="deleteTask">Delete</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'TaskItem',
  props: {
    task: {
      type: Object as PropType<{ title: string; description: string }>,
      required: true,
    },
  },
  emits: ['delete-task'],
  methods: {
    deleteTask() {
      this.$emit('delete-task');
    },
  },
});
</script>

<style scoped>
.task-item {
  border: 1px solid #ccc;
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 4px;
}

button {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #ff1a1a;
}
</style>
