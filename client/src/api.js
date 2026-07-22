import axios from 'axios'

const API_BASE_URL = 'http://localhost:8001/api'
const TOKEN_KEY = 'auth_token'

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token && config.url && config.url.startsWith(API_BASE_URL)) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const api = {
  async login(username, password) {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, { username, password })
    localStorage.setItem(TOKEN_KEY, response.data.access_token)
    return response.data
  },

  async getCurrentUser() {
    const response = await axios.get(`${API_BASE_URL}/auth/me`)
    return response.data
  },

  async getInventory(filters = {}) {
    const params = new URLSearchParams()
    if (filters.warehouse && filters.warehouse !== 'all') params.append('warehouse', filters.warehouse)
    if (filters.category && filters.category !== 'all') params.append('category', filters.category)

    const response = await axios.get(`${API_BASE_URL}/inventory?${params.toString()}`)
    return response.data
  },

  async getInventoryItem(id) {
    const response = await axios.get(`${API_BASE_URL}/inventory/${id}`)
    return response.data
  },

  async getOrders(filters = {}) {
    const params = new URLSearchParams()
    if (filters.warehouse && filters.warehouse !== 'all') params.append('warehouse', filters.warehouse)
    if (filters.category && filters.category !== 'all') params.append('category', filters.category)
    if (filters.status && filters.status !== 'all') params.append('status', filters.status)
    if (filters.month && filters.month !== 'all') params.append('month', filters.month)

    const response = await axios.get(`${API_BASE_URL}/orders?${params.toString()}`)
    return response.data
  },

  async getOrder(id) {
    const response = await axios.get(`${API_BASE_URL}/orders/${id}`)
    return response.data
  },

  async getDemandForecasts() {
    const response = await axios.get(`${API_BASE_URL}/demand`)
    return response.data
  },

  async getBacklog() {
    const response = await axios.get(`${API_BASE_URL}/backlog`)
    return response.data
  },

  async getDashboardSummary(filters = {}) {
    const params = new URLSearchParams()
    if (filters.warehouse && filters.warehouse !== 'all') params.append('warehouse', filters.warehouse)
    if (filters.category && filters.category !== 'all') params.append('category', filters.category)
    if (filters.status && filters.status !== 'all') params.append('status', filters.status)
    if (filters.month && filters.month !== 'all') params.append('month', filters.month)

    const response = await axios.get(`${API_BASE_URL}/dashboard/summary?${params.toString()}`)
    return response.data
  },

  async getSpendingSummary() {
    const response = await axios.get(`${API_BASE_URL}/spending/summary`)
    return response.data
  },

  async getMonthlySpending() {
    const response = await axios.get(`${API_BASE_URL}/spending/monthly`)
    return response.data
  },

  async getCategorySpending() {
    const response = await axios.get(`${API_BASE_URL}/spending/categories`)
    return response.data
  },

  async getTransactions() {
    const response = await axios.get(`${API_BASE_URL}/spending/transactions`)
    return response.data
  },

  async getTasks() {
    const response = await axios.get(`${API_BASE_URL}/tasks`)
    return response.data
  },

  async createTask(taskData) {
    const response = await axios.post(`${API_BASE_URL}/tasks`, taskData)
    return response.data
  },

  async deleteTask(taskId) {
    const response = await axios.delete(`${API_BASE_URL}/tasks/${taskId}`)
    return response.data
  },

  async toggleTask(taskId) {
    const response = await axios.patch(`${API_BASE_URL}/tasks/${taskId}`)
    return response.data
  },

  async createPurchaseOrder(purchaseOrderData) {
    const response = await axios.post(`${API_BASE_URL}/purchase-orders`, purchaseOrderData)
    return response.data
  },

  async getPurchaseOrderByBacklogItem(backlogItemId) {
    const response = await axios.get(`${API_BASE_URL}/purchase-orders/${backlogItemId}`)
    return response.data
  }
}
