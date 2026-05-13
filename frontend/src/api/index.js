import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => {
    const data = res.data
    if (data && typeof data === 'object' && 'count' in data && 'results' in data) {
      return data.results
    }
    return data
  },
  (err) => {
    const data = err.response?.data
    if (data && typeof data === 'object') {
      const messages = []
      for (const [key, value] of Object.entries(data)) {
        if (Array.isArray(value)) {
          messages.push(...value)
        } else if (typeof value === 'string') {
          messages.push(value)
        }
      }
      if (messages.length) {
        return Promise.reject(new Error(messages.join('; ')))
      }
    }
    return Promise.reject(new Error(err.message))
  }
)

export default api
