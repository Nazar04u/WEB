// src/utils/tokenUtils.js
import { jwtDecode }  from 'jwt-decode';  // Ensure jwt-decode is installed: npm install jwt-decode
import api from '../services/api';

// Function to get refresh token from local storage
export const getRefreshToken = () => {
    return localStorage.getItem('refresh_token');
};

// Function to check if the token is expired
export const isTokenExpired = (token) => {
    if (!token) return true; // Token is invalid if not present
    const decodedToken = jwtDecode(token);
    return decodedToken.exp * 1000 < Date.now(); // Compare expiration time
};

// Function to refresh the access token
export const refreshAccessToken = async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken || isTokenExpired(refreshToken)) return null;

    try {
        const response = await api.post('/api/token/refresh/', {
            refresh: refreshToken,
        });
        // Save new access token
        localStorage.setItem('access_token', response.data.access);
        return response.data.access;
    } catch (error) {
        console.error("Failed to refresh access token:", error);
        return null;
    }
};
