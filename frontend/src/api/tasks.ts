import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const fetchTasks = async () => {
  try {
    const response = await axios.get(`${API_URL}/tasks/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw error;
  }
};

export const createTask = async (task: { title: string; description: string }) => {
  try {
    const response = await axios.post(`${API_URL}/tasks/create/`, task);
    return response.data;
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
};

export const updateTask = async (taskId: number, task: { title: string; description: string }) => {
  try {
    const response = await axios.put(`${API_URL}/tasks/update/${taskId}/`, task);
    return response.data;
  } catch (error) {
    console.error('Error updating task:', error);
    throw error;
  }
};

export const deleteTask = async (taskId: number) => {
  try {
    const response = await axios.delete(`${API_URL}/tasks/delete/${taskId}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting task:', error);
    throw error;
  }
};
