import { reactive } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
export const session = reactive({ user: null, ready: false, revision: 0 })

class ApiService {
  async request(endpoint, options = {}) {
    const headers = { ...options.headers }
    if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json'
    const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers, credentials: 'include' })
    const body = await response.json().catch(() => null)
    if (!response.ok) {
      if (response.status === 401) {
        session.user = null
        session.revision++
      }
      const detail = typeof body?.detail === 'string' ? body.detail : 'Die Anfrage konnte nicht verarbeitet werden.'
      throw new Error(detail)
    }
    return body
  }
  async loadSession() {
    session.user = await this.request('/auth/me')
    session.ready = true
  }
  async login(credentials) {
    session.user = await this.request('/auth/login', { method: 'POST', body: JSON.stringify(credentials) })
    session.revision++
  }
  async register(credentials) {
    session.user = await this.request('/auth/register', { method: 'POST', body: JSON.stringify(credentials) })
    session.revision++
  }
  async logout() {
    await this.request('/auth/logout', { method: 'POST' })
    session.user = null
    session.revision++
  }
  getRecipes(favourites = false) { return this.request(`/recipes/${favourites ? '?favourites=true' : ''}`) }
  getTags() { return this.request('/tags/') }
  setFavourite(id, starred) { return this.request(`/recipes/${id}/favourite`, { method: starred ? 'PUT' : 'DELETE' }) }
  getRecipe(id) { return this.request(`/recipes/${id}`) }
  createRecipe(recipe) { return this.request('/recipes/', { method: 'POST', body: JSON.stringify(recipe) }) }
  updateRecipe(id, recipe) { return this.request(`/recipes/${id}`, { method: 'PUT', body: JSON.stringify(recipe) }) }
  deleteRecipe(id) { return this.request(`/recipes/${id}`, { method: 'DELETE' }) }
  uploadImage(id, file) {
    const body = new FormData()
    body.append('image', file)
    return this.request(`/recipes/${id}/image`, { method: 'POST', body })
  }
  removeImage(id) { return this.request(`/recipes/${id}/image`, { method: 'DELETE' }) }
  imageUrl(recipe) { return recipe.image_url ? `${API_BASE_URL}/recipes/${recipe.id}/image` : null }
}
export default new ApiService()
