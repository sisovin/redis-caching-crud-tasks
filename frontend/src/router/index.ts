import { createRouter, createWebHistory } from 'vue-router';
import TaskForm from '../components/TaskForm.vue';
import TaskList from '../components/TaskList.vue';

const routes = [
  {
    path: '/',
    name: 'TaskList',
    component: TaskList,
  },
  {
    path: '/add',
    name: 'TaskForm',
    component: TaskForm,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
