<template>
  <div>
    <ul>
      <li v-for="(task, index) in tasks" :key="index">
        <TaskItem :task="task" @delete-task="deleteTask(index)" />
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import TaskItem from './TaskItem.vue';

export default defineComponent({
  name: 'TaskList',
  components: {
    TaskItem,
  },
  props: {
    tasks: {
      type: Array as PropType<{ title: string; description: string }[]>,
      required: true,
    },
  },
  emits: ['delete-task'],
  methods: {
    deleteTask(index: number) {
      this.$emit('delete-task', index);
    },
  },
});
</script>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin: 10px 0;
}
</style>
