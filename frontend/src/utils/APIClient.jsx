import axios from 'axios';
import api_url from './Config';

const axiosClient = axios.create({
    baseURL: api_url,
    headers: {
        "Content-Type": "application/json",
    },
});

const api = {
    get: (url) => {
        return axiosClient.get(url)
            .then(response => response.data)
            .catch(error => {
                console.error('GET Error:', error);
                throw error;
            });
    },

    post: (url, data) => {
        return axiosClient.post(url, data)
            .then(response => response.data)
            .catch(error => {
                console.error('POST Error:', error);
                throw error;
            });
    },
};

export default api;
