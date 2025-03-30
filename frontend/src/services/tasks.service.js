import api from './api';

const TaskService = {
  getTasks() {
    return api.get('/tasks');
  },
  getTask(id) {
    return api.get(`/tasks/${id}`);
  },
  createTask(task) {
    return api.post('/tasks', task);
  },
  updateTask(id, task) {
    return api.put(`/tasks/${id}`, task);
  },
  deleteTask(id) {
    return api.delete(`/tasks/${id}`);
  },
};

export default TaskService;
