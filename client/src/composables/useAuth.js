import { ref, computed } from 'vue'
import { useI18n } from './useI18n'
import { api } from '../api'

const TOKEN_KEY = 'auth_token'

// Base mock profile data (language-independent), merged with real API user data
const baseUserData = {
  id: 1,
  email: 'john.doe@catalystcomponents.com',
  phone: '+1 (111) 111-1111',
  avatar: null,
  joinDate: '2022-03-15',
  tasks: []
}

const apiUser = ref(null)
const hasToken = ref(!!localStorage.getItem(TOKEN_KEY))

const createCurrentUser = () => {
  const { currentLocale } = useI18n()

  return computed(() => {
    const isJapanese = currentLocale.value === 'ja'

    const mockTasks = isJapanese ? [
      {
        id: 1,
        title: '第4四半期の在庫レベルを確認',
        priority: 'high',
        dueDate: '2025-10-08',
        status: 'pending'
      },
      {
        id: 2,
        title: '東京倉庫の注文を承認',
        priority: 'medium',
        dueDate: '2025-10-06',
        status: 'pending'
      },
      {
        id: 3,
        title: '回路基板の再注文点を更新',
        priority: 'medium',
        dueDate: '2025-10-10',
        status: 'pending'
      },
      {
        id: 4,
        title: '月次支出レポートを確認',
        priority: 'low',
        dueDate: '2025-10-15',
        status: 'pending'
      }
    ] : [
      {
        id: 1,
        title: 'Review Q4 inventory levels',
        priority: 'high',
        dueDate: '2025-10-08',
        status: 'pending'
      },
      {
        id: 2,
        title: 'Approve Tokyo warehouse orders',
        priority: 'medium',
        dueDate: '2025-10-06',
        status: 'pending'
      },
      {
        id: 3,
        title: 'Update reorder points for Circuit Boards',
        priority: 'medium',
        dueDate: '2025-10-10',
        status: 'pending'
      },
      {
        id: 4,
        title: 'Review monthly spending report',
        priority: 'low',
        dueDate: '2025-10-15',
        status: 'pending'
      }
    ]

    const fallbackName = isJapanese ? '田中 太郎' : 'John Doe'
    const fallbackJobTitle = isJapanese ? 'オペレーションマネージャー' : 'Operations Manager'

    return {
      ...baseUserData,
      username: apiUser.value?.username,
      name: apiUser.value?.full_name || fallbackName,
      jobTitle: apiUser.value?.role || fallbackJobTitle,
      department: isJapanese ? 'サプライチェーン運営部' : 'Supply Chain Operations',
      location: isJapanese ? 'サンフランシスコ' : 'San Francisco',
      tasks: mockTasks
    }
  })
}

const currentUser = createCurrentUser()

const isAuthenticated = computed(() => hasToken.value)

const fetchCurrentUser = async () => {
  try {
    apiUser.value = await api.getCurrentUser()
  } catch (err) {
    console.error('Failed to load current user:', err)
    apiUser.value = null
  }
}

export function useAuth() {
  const login = async (username, password) => {
    await api.login(username, password)
    hasToken.value = true
    await fetchCurrentUser()
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY)
    hasToken.value = false
    apiUser.value = null
    window.location.href = '/login'
  }

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
  }

  return {
    currentUser,
    isAuthenticated,
    login,
    logout,
    getInitials,
    fetchCurrentUser
  }
}
