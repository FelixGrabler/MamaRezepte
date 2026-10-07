<template>
  <div>
    <router-link to="/" class="back-button">← Zur Übersicht</router-link>
    <p v-if="loading" class="loading">Rezept wird geladen…</p>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>
    <article v-else-if="recipe" class="recipe-detail">
      <div class="page-heading"><h1>{{ recipe.title }}</h1><span v-if="!recipe.is_public" class="privacy-badge">🔒 Nur für dich</span></div>
      <div class="actions">
        <router-link v-if="recipe.can_edit && !recipe.parent_id" class="primary-button" :to="`/recipe/${recipe.id}/edit`">Bearbeiten</router-link>
        <button v-if="session.user && !recipe.parent_id" class="star-button" :class="{ starred: recipe.is_favourite }" :aria-pressed="recipe.is_favourite" :disabled="starBusy" @click="toggleFavourite">{{ recipe.is_favourite ? '★ Aus Favouriten entfernen' : '☆ Zu Favouriten hinzufügen' }}</button>
        <button v-if="recipe.can_edit && !recipe.parent_id" class="danger-button" @click="confirmDelete = !confirmDelete">Löschen</button>
      </div>
      <div v-if="confirmDelete" class="delete-confirm" role="alert">
        <p>Dieses Rezept und alle seine Teile wirklich löschen?</p>
        <button class="danger-button" :disabled="busy" @click="remove">Ja, löschen</button>
        <button class="secondary-button" @click="confirmDelete = false">Abbrechen</button>
      </div>
      <p v-if="actionError" class="error" role="alert">{{ actionError }}</p>
      <div v-if="recipe.image_path" class="recipe-detail-image"><img :src="api.imageUrl(recipe)" :alt="recipe.title" /></div>
      <router-link class="category-badge" :to="{ path: '/', query: { category: recipe.category } }">{{ recipe.category }}</router-link>
      <div class="recipe-tags"><router-link v-for="tag in recipe.tags" :key="tag" class="tag" :to="{ path: '/', query: { tag } }">{{ tag }}</router-link></div>
      <div class="portion-control" aria-label="Portionen einstellen">
        <label for="view-servings">Portionen</label>
        <button aria-label="Eine Portion weniger" :disabled="viewServings <= 1" @click="viewServings--">−</button>
        <input id="view-servings" :value="viewServings" @change="setServings" type="number" min="1" max="1000" step="1" />
        <button aria-label="Eine Portion mehr" :disabled="viewServings >= 1000" @click="viewServings++">+</button>
        <button v-if="viewServings !== recipe.servings" class="secondary-button" @click="viewServings = recipe.servings">Zurück auf {{ recipe.servings }}</button>
      </div>
      <p class="field-help">Zutatenmengen für {{ viewServings }} Portionen. Ohne Mengenangabe bleiben Zutaten unverändert.</p>
      <section class="all-ingredients-section"><h2>Zutaten</h2>
        <div v-for="part in sections" :key="part.id" class="ingredient-group">
          <h3 v-if="sections.length > 1">{{ part.title }}</h3>
          <ul class="ingredients-list"><li v-for="(ingredient, i) in part.ingredients" :key="i">{{ formatIngredient(ingredient) }}</li></ul>
        </div>
      </section>
      <section class="all-instructions-section"><h2>Zubereitung</h2>
        <div v-for="part in sections" :key="part.id" class="instruction-group">
          <h3 v-if="sections.length > 1">{{ part.title }}</h3>
          <div class="instructions">{{ part.instructions }}</div>
        </div>
      </section>
      <p v-if="recipe.parent_id"><router-link :to="`/recipe/${recipe.parent_id}`">Zum Hauptrezept</router-link></p>
    </article>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { session } from '../services/api'
const props = defineProps(['id'])
const router = useRouter()
const viewServings = ref(4), starBusy = ref(false)
const recipe = ref(null), loading = ref(true), error = ref(''), actionError = ref(''), confirmDelete = ref(false), busy = ref(false)
function flatten(record) { return [...record.parts.flatMap(flatten), record] }
const sections = computed(() => recipe.value ? flatten(recipe.value) : [])
function formatIngredient(i) { return [i.amount == null ? '' : new Intl.NumberFormat('de-AT', { maximumFractionDigits: 6 }).format(i.amount * viewServings.value / recipe.value.servings), i.unit, i.ingredient].filter(v => v !== '' && v != null).join(' ') }
function setServings(event) {
  const amount = Number(event.target.value)
  if (Number.isInteger(amount) && amount >= 1 && amount <= 1000) viewServings.value = amount
  event.target.value = viewServings.value
}
async function toggleFavourite() {
  starBusy.value = true
  actionError.value = ''
  try { const result = await api.setFavourite(props.id, !recipe.value.is_favourite); recipe.value.is_favourite = result.is_favourite }
  catch (e) { actionError.value = e.message }
  finally { starBusy.value = false }
}
async function remove() {
  busy.value = true
  try { await api.deleteRecipe(props.id); router.push('/') } catch (e) { actionError.value = e.message }
  finally { busy.value = false }
}
onMounted(async () => {
  try { recipe.value = await api.getRecipe(props.id); viewServings.value = recipe.value.servings } catch (e) { error.value = e.message }
  finally { loading.value = false }
})
</script>
