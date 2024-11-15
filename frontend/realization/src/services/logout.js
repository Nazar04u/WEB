import axios from 'axios';
import Cookies from 'js-cookie'; // You may need to install this package

const logout = async () => {
    try {
        // Get the CSRF token from cookies
        const csrfToken = Cookies.get('csrftoken');

        // Send the logout request
        const response = await axios.post('http://localhost:8001/logout/', {}, {
            headers: {
                'csrftoken': csrfToken,
                'Content-Type': 'application/json',
            },
        });

        // Handle successful logout response
        console.log(response.data);
        // Optionally, redirect to the login page or show a success message
    } catch (error) {
        console.error('Error logging out:', error.response ? error.response.data : error.message);
    }
};

export default logout;
