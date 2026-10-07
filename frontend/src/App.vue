<template>
  <div>
    <header ref="header" class="header" @keydown.esc="closeMenu(true)">
      <router-link to="/" class="brand">🍳 Mama's Rezepte</router-link>
      <button ref="menuButton" class="menu-toggle" :aria-label="menuOpen ? 'Menü schließen' : 'Menü öffnen'" :aria-expanded="menuOpen" aria-controls="main-navigation" @click="menuOpen = !menuOpen">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
          <path v-if="menuOpen" d="m6 6 12 12M6 18 18 6" />
          <path v-else d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <nav id="main-navigation" aria-label="Hauptnavigation" :class="{ 'is-open': menuOpen }" @click="closeMenu()">
        <router-link class="nav-link" to="/">Alle Rezepte</router-link>
        <template v-if="session.user">
          <router-link class="nav-link" to="/favourites">★ Favouriten</router-link>
          <router-link class="nav-link" to="/new">Rezept hinzufügen</router-link>
          <span>{{ session.user.username }}</span>
          <button class="nav-link" @click="logout" :disabled="busy">Abmelden</button>
        </template>
        <template v-else><router-link class="nav-link" to="/login">Anmelden</router-link><router-link class="nav-link" to="/register">Registrieren</router-link></template>
      </nav>
    </header>
    <main class="main" :class="{ 'main--browse': route.path === '/' || route.path === '/favourites' }">
      <p v-if="error" class="error" role="alert">{{ error }} <button @click="load">Erneut versuchen</button></p>
      <router-view v-if="session.ready" :key="$route.fullPath + ':' + session.revision" />
      <p v-else-if="!error" class="loading">Wird geladen…</p>
    </main>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api, { session } from './services/api'
const router = useRouter()
const route = useRoute()
const menuOpen = ref(false), header = ref(null), menuButton = ref(null)
const error = ref('')
const busy = ref(false)
function closeMenu(returnFocus = false) {
  menuOpen.value = false
  if (returnFocus) menuButton.value?.focus()
}
function closeOutside(event) {
  if (!header.value?.contains(event.target)) closeMenu()
}
watch(() => route.fullPath, () => closeMenu())
async function load() {
  error.value = ''
  try { await api.loadSession() } catch (e) { error.value = e.message }
}
async function logout() {
  busy.value = true
  try { await api.logout(); router.push('/') } catch (e) { error.value = e.message }
  finally { busy.value = false }
}
onMounted(() => { load(); document.addEventListener('pointerdown', closeOutside) })
onUnmounted(() => document.removeEventListener('pointerdown', closeOutside))
</script>
