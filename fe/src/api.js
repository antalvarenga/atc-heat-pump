import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:5010/',
    // headers: {'X-Custom-Header': 'foobar'}
  });


export const getHourlyData = async (params) => {
    const resp = await api.get('/aggregated/hourly', { params })
    return resp.data
}

export const getDailyData = async (params) => {
    const resp = await api.get('/aggregated/free', { params })
    return resp.data
}