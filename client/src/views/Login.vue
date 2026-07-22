<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const route = useRoute()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const error = ref(null)
const submitting = ref(false)
const usernameInput = ref(null)

const handleSubmit = async () => {
  if (submitting.value) return
  error.value = null
  submitting.value = true
  try {
    await login(username.value, password.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    if (err.response && err.response.status === 401) {
      error.value = err.response.data?.detail || 'Incorrect username or password'
    } else {
      error.value = 'Unable to sign in. Please try again.'
    }
    console.error(err)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  usernameInput.value?.focus()
})
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>Factory Inventory</h1>
        <p>Sign in to your account</p>
      </div>

      <form @submit.prevent="handleSubmit" novalidate>
        <div class="form-field">
          <label for="username">Username</label>
          <input
            id="username"
            ref="usernameInput"
            v-model="username"
            type="text"
            autocomplete="username"
            aria-label="Username"
            :disabled="submitting"
            required
          />
        </div>

        <div class="form-field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            aria-label="Password"
            :disabled="submitting"
            required
          />
        </div>

        <div v-if="error" class="error-message" role="alert">
          {{ error }}
        </div>

        <button type="submit" class="submit-btn" :disabled="submitting">
          {{ submitting ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <div class="demo-hint">
        <p>Demo credentials</p>
        <p><strong>admin</strong> / admin123</p>
        <p><strong>manager</strong> / manager123</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  padding: 1.5rem;
}

.login-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 1.75rem;
}

.login-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 0.375rem;
}

.login-header p {
  color: #64748b;
  font-size: 0.938rem;
}

.form-field {
  margin-bottom: 1.25rem;
}

.form-field label {
  display: block;
  font-size: 0.813rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.375rem;
}

.form-field input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.938rem;
  color: #0f172a;
  background: #ffffff;
  transition: border-color 0.2s ease;
}

.form-field input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-field input:disabled {
  background: #f8fafc;
  color: #64748b;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
}

.submit-btn {
  width: 100%;
  padding: 0.688rem 1rem;
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background: #1e293b;
}

.submit-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.demo-hint {
  margin-top: 1.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid #e2e8f0;
  text-align: center;
  color: #64748b;
  font-size: 0.813rem;
}

.demo-hint p {
  margin-bottom: 0.25rem;
}
</style>
