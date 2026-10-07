<template>
  <section class="form-panel login-panel">
    <h1>Anmelden</h1>
    <p>Verwende dein bestehendes Grabler.me-Konto.</p>
    <form @submit.prevent="login">
      <label>Benutzername<input v-model="username" required maxlength="64" autocomplete="username" /></label>
      <label>Passwort<input v-model="password" required type="password" maxlength="128" autocomplete="current-password" /></label>
      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <button class="primary-button" :disabled="busy">{{ busy ? 'Anmelden…' : 'Anmelden' }}</button>
    </form>
    <p>Noch kein Konto? <router-link :to="{ path: '/register', query: route.query }">Registrieren</router-link></p>
    <p>Mit einem Konto kannst du eigene Rezepte erstellen und private Rezepte speichern.</p>
  </section>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'
const username = ref(''), password = ref(''), error = ref(''), busy = ref(false)
const router = useRouter(), route = useRoute()
async function login() {
  busy.value = true
  error.value = ''
  try {
    await api.login({ username: username.value, password: password.value })
    const next = typeof route.query.next === 'string' ? route.query.next : '/'
    router.replace(next.startsWith('/') && !next.startsWith('//') ? next : '/')
  } catch (e) { error.value = e.message }
  finally { password.value = ''; busy.value = false }
}
</script>
