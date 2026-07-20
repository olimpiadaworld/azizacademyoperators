import axios from 'axios'

function appendApiPath(url) {
  const value = String(url || '').trim()
  if (!value) return ''
  const withoutTrailingSlash = value.replace(/\/+$/, '')
  return withoutTrailingSlash.endsWith('/api') ? `${withoutTrailingSlash}/` : `${withoutTrailingSlash}/api/`
}

function buildDefaultBaseUrl() {
  const { protocol, hostname, origin } = window.location
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:8000/api/`
  }
  return appendApiPath(origin)
}

const runtimeBaseUrl = window.APP_CONFIG?.apiBaseUrl || window.APP_CONFIG?.apiUrl || ''
const rawBaseUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || runtimeBaseUrl || buildDefaultBaseUrl()
const normalizedBaseUrl = appendApiPath(rawBaseUrl)

const client = axios.create({
  baseURL: normalizedBaseUrl,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config || {}
    const refresh = localStorage.getItem('refresh')

    if (error.response?.status === 401 && refresh && !original._retry && !String(original.url || '').includes('auth/refresh/')) {
      original._retry = true
      try {
        const { data } = await axios.post(`${normalizedBaseUrl}auth/refresh/`, { refresh })
        localStorage.setItem('access', data.access)
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${data.access}`
        return client(original)
      } catch (refreshError) {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        localStorage.removeItem('user')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default client
