import TaskService from '../services/tasks.service';

const state = {
  tasks: [],
  task: null,
};

const mutations = {
  SET_TASKS(state, tasks) {
    state.tasks = tasks;
  },
  SET_TASK(state, task) {
    state.task = task;
  },
  ADD_TASK(state, task) {
    state.tasks.push(task);
  },
  UPDATE_TASK(state, updatedTask) {
    const index = state.tasks.findIndex(task => task.id === updatedTask.id);
    if (index !== -1) {
      state.tasks.splice(index, 1, updatedTask);
    }
  },
  DELETE_TASK(state, taskId) {
    state.tasks = state.tasks.filter(task => task.id !== taskId);
  },
};

const actions = {
  async fetchTasks({ commit }) {
    const response = await TaskService.getTasks();
    commit('SET_TASKS', response.data);
  },
  async fetchTask({ commit }, taskId) {
    const response = await TaskService.getTask(taskId);
    commit('SET_TASK', response.data);
  },
  async createTask({ commit }, task) {
    const response = await TaskService.createTask(task);
    commit('ADD_TASK', response.data);
  },
  async updateTask({ commit }, task) {
    const response = await TaskService.updateTask(task.id, task);
    commit('UPDATE_TASK', response.data);
  },
  async deleteTask({ commit }, taskId) {
    await TaskService.deleteTask(taskId);
    commit('DELETE_TASK', taskId);
  },
};

const getters = {
  tasks: state => state.tasks,
  task: state => state.task,
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
