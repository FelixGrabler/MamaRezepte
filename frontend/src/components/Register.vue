<template>
  <section class="form-panel login-panel">
    <h1>Registrieren</h1>
    <p>Dein neues Grabler.me-Konto funktioniert auch auf den anderen Grabler.me-Websites.</p>
    <form @submit.prevent="register">
      <label>Benutzername<input v-model="username" required maxlength="64" pattern="[A-Za-z0-9_.-]+" autocomplete="username" /></label>
      <p class="field-help">Buchstaben ohne Umlaute, Zahlen, Punkt, Bindestrich und Unterstrich.</p>
      <label>Passwort<input v-model="password" required type="password" minlength="8" maxlength="72" autocomplete="new-password" /></label>
      <label>Passwort wiederholen<input v-model="confirmation" required type="password" minlength="8" maxlength="72" autocomplete="new-password" /></label>
      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <button class="primary-button" :disabled="busy">{{ busy ? 'Registrieren…' : 'Registrieren' }}</button>
    </form>
    <p>Schon ein Konto? <router-link :to="{ path: '/login', query: route.query }">Anmelden</router-link></p>
  </section>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'
const username = ref(''), password = ref(''), confirmation = ref(''), error = ref(''), busy = ref(false)
const router = useRouter(), route = useRoute()
async function register() {
  error.value = ''
  if (password.value !== confirmation.value) { error.value = 'Die Passwörter stimmen nicht überein.'; return }
  if (new TextEncoder().encode(password.value).length > 72) { error.value = 'Bitte ein kürzeres Passwort verwenden.'; return }
  busy.value = true
  try {
    await api.register({ username: username.value, password: password.value })
    const next = typeof route.query.next === 'string' ? route.query.next : '/'
    router.replace(next.startsWith('/') && !next.startsWith('//') ? next : '/')
  } catch (e) { error.value = e.message }
  finally { password.value = ''; confirmation.value = ''; busy.value = false }
}
</script>
