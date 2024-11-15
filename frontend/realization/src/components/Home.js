import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import axios from 'axios';
import './Home.css';

const Home = () => {
    const [logoutMessage, setLogoutMessage] = useState('');
    const [functionInput, setFunctionInput] = useState('x**2');
    const [lowerBound, setLowerBound] = useState(0);
    const [upperBound, setUpperBound] = useState(1);
    const [result, setResult] = useState(null);
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [taskStatus, setTaskStatus] = useState(null);
    const [progressPercent, setProgressPercent] = useState(null);
    const [taskId, setTaskId] = useState(null);
    const [isUserCanceled, setIsUserCanceled] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Reset `isUserCanceled` when a new task ID is set
        if (taskId) {
            setIsUserCanceled(false);
        }
    }, [taskId]);

    const handleLogout = async () => {
        try {
            const csrfToken = Cookies.get('csrftoken');
            await axios.post('http://localhost:8001/logout/', {}, {
                headers: { 'X-CSRFToken': csrfToken },
                withCredentials: true,
            });
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setLogoutMessage("You have successfully logged out.");
            navigate('/login');
        } catch (error) {
            console.error("Error during logout:", error.response ? error.response.data : error.message);
            setLogoutMessage("An error occurred while logging out.");
        }
    };

    const handleCancelTask = async () => {
        const token = localStorage.getItem('access_token');
        if (!taskId) {
            alert("No task is currently running.");
            return;
        }
        try {
            await api.post(`/cancel_task/${taskId}/`, {}, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setIsUserCanceled(true);
            setTaskId(null);
            alert("Task was successfully canceled.");
        } catch (error) {
            console.error("Error canceling task:", error);
            alert("An error occurred while attempting to cancel the task.");
        }
    };

    const handleIntegration = async () => {
        const token = localStorage.getItem('access_token');
        if (!functionInput || lowerBound >= upperBound) {
            alert("Please ensure the function is valid and the lower bound is less than the upper bound.");
            return;
        }

        // Clear any previous task info and reset state
        setIsLoading(true);
        setTaskStatus("Starting...");
        setProgressPercent(null);
        setResult(null);
        setTaskId(null);

        try {
            const response = await api.post('', {
                function: functionInput,
                lower_bound: lowerBound,
                upper_bound: upperBound,
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });

            setTaskId(response.data.task_id);
            alert(`Task started with ID: ${response.data.task_id}`);

            const intervalId = setInterval(async () => {
                try {
                    const statusResponse = await api.get(`/task-status/${response.data.task_id}/`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    setTaskStatus(statusResponse.data.status);
                    setProgressPercent(statusResponse.data.percent_complete || null);

                    if (statusResponse.data.status === 'SUCCESS') {
                        clearInterval(intervalId);
                        if (isUserCanceled) {
                            setTaskStatus("Canceled");
                            alert("Task was canceled by the user.");
                        } else if (statusResponse.data.result) {
                            setResult(statusResponse.data.result);
                            alert(`Estimated Area: ${statusResponse.data.result.estimated_area}`);
                        } else {
                            alert("Task completed but no result was returned.");
                            setTaskStatus("No result available.");
                        }
                    } else if (statusResponse.data.status === 'FAILURE') {
                        clearInterval(intervalId);
                        setTaskStatus('Failed to complete the task.');
                    }
                } catch (error) {
                    clearInterval(intervalId);
                    console.error("Error fetching task status:", error);
                    alert("Error fetching task status.");
                }
            }, 2000);

            // Cleanup function to clear the interval if component unmounts or task finishes
            return () => clearInterval(intervalId);
        } catch (error) {
            console.error("Error during integration:", error);
            alert("An error occurred during integration. Please check your function and bounds.");
            if (error.response && error.response.status === 401) {
                navigate('/login');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const fetchHistory = async () => {
        const token = localStorage.getItem('access_token');
        try {
            const response = await api.get('', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setHistory(response.data);
        } catch (error) {
            console.error("Error fetching history:", error);
            if (error.response && error.response.status === 401) {
                navigate('/login');
            }
        }
    };

    useEffect(() => {
        fetchHistory();
    }, [navigate]);

    return (
        <div className="home-container">
            <h2>Monte Carlo Integration</h2>
            <div className="input-section">
                <label>Function (e.g., x**2):</label>
                <input type="text" value={functionInput} onChange={(e) => setFunctionInput(e.target.value)} />
                <label>Lower Bound:</label>
                <input type="number" value={lowerBound} onChange={(e) => setLowerBound(Number(e.target.value))} />
                <label>Upper Bound:</label>
                <input type="number" value={upperBound} onChange={(e) => setUpperBound(Number(e.target.value))} />
                <button onClick={handleIntegration} disabled={isLoading}>
                    {isLoading ? 'Calculating...' : 'Calculate Area'}
                </button>
            </div>

            {taskStatus && (
                <div className="task-status">
                    <p>Status: {taskStatus}</p>
                    {progressPercent !== null && <p>Progress: {progressPercent}%</p>}
                </div>
            )}
            {taskStatus && taskStatus !== 'SUCCESS' && taskStatus !== 'FAILURE' && (
                <button onClick={handleCancelTask} disabled={!taskId || isLoading || isUserCanceled}>
                    Cancel Task
                </button>
            )}

            {result && !isUserCanceled && (
                <div className="result-card">
                    <h3>Results:</h3>
                    <p>Function: {result.function}, a={result.lower_bound}, b={result.upper_bound}</p>
                    <p>Estimated Area: {result.estimated_area}</p>
                    <p>Time Taken: {result.time_needed} seconds</p>
                    {result.graphic_url && <img src={result.graphic_url} alt="Integration Graphic" className="result-image" />}
                </div>
            )}

            <h3>Your Solution History:</h3>
            <div className="history-grid">
                {history.map((item, index) => (
                    <div className="history-card" key={index}>
                        <p>Function: {item.function}, a={item.lower_bound}, b={item.upper_bound}</p>
                        <p>Estimated Area: {item.estimated_area}</p>
                        <p>Time Taken: {item.time_needed} seconds</p>
                        {item.graphic_url && <img src={item.graphic_url} alt="Integration Graphic" className="history-image" />}
                    </div>
                ))}
            </div>

            <button onClick={handleLogout} className="logout-button">Logout</button>
            {logoutMessage && <p>{logoutMessage}</p>}
        </div>
    );
};

export default Home;
