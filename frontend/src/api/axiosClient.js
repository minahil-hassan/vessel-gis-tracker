// src/api/axiosClient.js

import axios from 'axios';

const axiosClient = axios.create({
  baseURL: 'http://localhost:8000/api', // Adjust this if you change backend routing
  timeout: 180000, // 3 minutes
});

export default axiosClient;
