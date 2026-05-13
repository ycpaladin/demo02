import axios, { type AxiosInstance } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => {
    const data: unknown = res.data
    if (data && typeof data === 'object' && 'count' in data && 'results' in data) {
      return (data as { results: unknown }).results
    }
    return data
  },
  (err) => {
    const data = err.response?.data
    if (data && typeof data === 'object') {
      const messages: string[] = []
      for (const [, value] of Object.entries(data)) {
        if (Array.isArray(value)) {
          messages.push(...(value as string[]))
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
