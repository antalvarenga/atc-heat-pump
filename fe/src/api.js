import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:5010/',
    // headers: {'X-Custom-Header': 'foobar'}
  });


export const getHourlyData = async (params) => {
    const resp = await api.get('/optimizeDaily/hourly', { params })
    console.log("api call")
    return resp.data
}