import Vue from 'vue';
import Router from 'vue-router';
import TasksView from './views/TasksView.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/tasks',
      name: 'Tasks',
      component: TasksView,
    },
  ],
});
