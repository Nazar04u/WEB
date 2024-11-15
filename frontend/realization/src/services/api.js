// services/api.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8001', // Base URL of your Django backend
    withCredentials: true, // Ensures cookies are sent with requests
});

// Request Interceptor to include access token in headers
api.interceptors.request.use(
    (config) => {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            config.headers['Authorization'] = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor to handle 401 errors and refresh token
api.interceptors.response.use(
    (response) => response, // Pass through if response is successful
    async (error) => {
        const originalRequest = error.config;

        // Check if the error is due to expired access token
        if (error.response && error.response.status === 403 && !originalRequest._retry) {
            originalRequest._retry = true; // Avoids infinite loop

            try {
                // Get refresh token from local storage
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    // Make a request to refresh the access token
                    const response = await axios.post('http://localhost:8001/api/token/refresh/', {
                        refresh: refreshToken,
                    });
                    const newAccessToken = response.data.access;
                    localStorage.setItem('access_token', newAccessToken);

                    // Update the original request's access token
                    originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

                    // Retry the original request with the new token
                    return api(originalRequest);
                } else {
                    throw new Error('No refresh token available.');
                }
            } catch (refreshError) {
                console.error("Token refresh failed", refreshError);
                // Optionally: Redirect to login page or logout
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
