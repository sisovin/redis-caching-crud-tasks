import { createStore } from 'vuex';

export default createStore({
  state: {
    tasks: [],
  },
  mutations: {
    setTasks(state, tasks) {
      state.tasks = tasks;
    },
    addTask(state, task) {
      state.tasks.push(task);
    },
    deleteTask(state, index) {
      state.tasks.splice(index, 1);
    },
  },
  actions: {
    fetchTasks({ commit }) {
      // Fetch tasks from the backend and commit the setTasks mutation
    },
    createTask({ commit }, task) {
      // Create a new task in the backend and commit the addTask mutation
    },
    removeTask({ commit }, index) {
      // Remove a task from the backend and commit the deleteTask mutation
    },
  },
  getters: {
    allTasks: (state) => state.tasks,
  },
});
