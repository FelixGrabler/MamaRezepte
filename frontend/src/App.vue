<template>
  <div>
    <header class="header">
      <router-link to="/" class="brand">🍳 Mama's Rezepte</router-link>
      <nav aria-label="Hauptnavigation">
        <router-link class="nav-link" to="/">Alle Rezepte</router-link>
        <template v-if="session.user">
          <router-link class="nav-link" to="/favourites">★ Favouriten</router-link>
          <router-link class="nav-link" to="/new">Rezept hinzufügen</router-link>
          <span>{{ session.user.username }}</span>
          <button class="nav-link" @click="logout" :disabled="busy">Abmelden</button>
        </template>
        <router-link v-else class="nav-link" to="/login">Anmelden</router-link>
      </nav>
    </header>
    <main class="main">
      <p v-if="error" class="error" role="alert">{{ error }} <button @click="load">Erneut versuchen</button></p>
      <router-view v-if="session.ready" :key="$route.fullPath + ':' + session.revision" />
      <p v-else-if="!error" class="loading">Wird geladen…</p>
    </main>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { session } from './services/api'
const router = useRouter()
const error = ref('')
const busy = ref(false)
async function load() {
  error.value = ''
  try { await api.loadSession() } catch (e) { error.value = e.message }
}
async function logout() {
  busy.value = true
  try { await api.logout(); router.push('/') } catch (e) { error.value = e.message }
  finally { busy.value = false }
}
onMounted(load)
</script>
