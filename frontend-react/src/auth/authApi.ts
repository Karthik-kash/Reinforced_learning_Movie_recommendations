import { apiRequest } from '../lib/api'

export type AuthUser = { user_id: string; email: string; username: string; is_demo: boolean }
export type AuthResponse = { access_token: string; token_type: string; user: AuthUser }

export const authApi = {
  register: (email: string, username: string, password: string) => apiRequest<AuthResponse>('/auth/register', { method: 'POST', body: JSON.stringify({ email, username, password }) }),
  login: (email: string, password: string) => apiRequest<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  demo: () => apiRequest<AuthResponse>('/auth/demo', { method: 'POST' }),
  me: () => apiRequest<AuthUser>('/auth/me'),
}
