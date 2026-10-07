<template>
  <div>
    <div class="page-heading"><h2>{{ favourites ? 'Favouriten' : 'Rezepte Übersicht' }}</h2><router-link v-if="session.user" class="primary-button" to="/new">+ Neues Rezept</router-link></div>
    <p v-if="favourites && !session.user">Bitte <router-link to="/login?next=/favourites">anmelden</router-link>, um deine Favouriten zu sehen.</p>
    <template v-else>
      <div class="search-container">
        <label class="sr-only" for="recipe-search">Rezept oder Zutat suchen</label>
        <input id="recipe-search" v-model="searchTerm" placeholder="Rezept oder Zutat suchen…" class="search-input" />
        <div class="filters">
          <label>Kategorie<select v-model="selectedCategory"><option value="">Alle Kategorien</option><option v-for="category in categories" :key="category">{{ category }}</option></select></label>
          <label v-if="session.user" class="checkbox-label"><input type="checkbox" v-model="onlyMine" /> Nur meine Rezepte</label>
        </div>
        <fieldset v-if="availableTags.length" class="tag-filters">
          <legend>Tags</legend>
          <label v-for="tag in availableTags" :key="tag" class="filter-tag" :class="{ selected: selectedTags.includes(tag) }"><input type="checkbox" v-model="selectedTags" :value="tag" />{{ tag }}</label>
          <p v-if="selectedTags.length > 1" class="field-help">Rezepte müssen alle ausgewählten Tags enthalten.</p>
        </fieldset>
        <button v-if="searchTerm || selectedCategory || selectedTags.length || onlyMine" class="secondary-button" @click="clearFilters">Filter zurücksetzen</button>
      </div>
      <div v-if="loading" class="loading">Rezepte werden geladen…</div>
      <div v-else-if="error" class="error" role="alert">{{ error }} <button @click="loadRecipes">Erneut versuchen</button></div>
      <p v-if="starError" class="error" role="alert">{{ starError }}</p>
      <div v-if="!loading && !error" class="recipe-grid">
        <article v-for="recipe in filteredRecipes" :key="recipe.id" class="recipe-card" :class="{ 'no-image': !recipe.image_path }">
          <router-link :to="`/recipe/${recipe.id}`" class="recipe-card-link">
            <div v-if="recipe.image_path" class="recipe-image"><img :src="api.imageUrl(recipe)" :alt="recipe.title" loading="lazy" /></div>
            <div class="recipe-content">
              <h3 class="recipe-title">{{ recipe.title }}</h3>
              <span class="category-badge">{{ recipe.category }}</span>
              <span v-if="!recipe.is_public" class="privacy-badge">🔒 Privat</span>
              <div v-if="recipe.tags.length" class="recipe-tags"><span v-for="tag in recipe.tags" :key="tag" class="tag">{{ tag }}</span></div>
            </div>
          </router-link>
          <button v-if="session.user" class="star-button card-star" :class="{ starred: recipe.is_favourite }" :aria-label="`${recipe.title}: ${recipe.is_favourite ? 'Aus Favouriten entfernen' : 'Zu Favouriten hinzufügen'}`" :aria-pressed="recipe.is_favourite" :disabled="starBusy.has(recipe.id)" @click="toggleFavourite(recipe)">{{ recipe.is_favourite ? '★' : '☆' }}</button>
        </article>
      </div>
      <p v-if="!loading && !error && !filteredRecipes.length" class="empty-state">{{ favourites && !recipes.length ? 'Noch keine Favouriten. Markiere ein Rezept mit einem Stern.' : 'Keine passenden Rezepte gefunden.' }}</p>
    </template>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api, { session } from '../services/api'
import { categories, tagKey } from '../services/catalogue'
const props = defineProps({ favourites: { type: Boolean, default: false } })
const route = useRoute()
const recipes = ref([]), loading = ref(true), error = ref(''), starError = ref(''), starBusy = ref(new Set())
const searchTerm = ref(''), onlyMine = ref(false)
const selectedCategory = ref(categories.includes(route.query.category) ? route.query.category : '')
const selectedTags = ref(Array.isArray(route.query.tag) ? route.query.tag : route.query.tag ? [route.query.tag] : [])
const availableTags = computed(() => [...new Map(recipes.value.flatMap(recipe => recipe.tags).map(tag => [tagKey(tag), tag])).values()].sort((a, b) => a.localeCompare(b, 'de-AT')))
function matches(recipe, term) {
  return recipe.title.toLowerCase().includes(term) || recipe.ingredients.some(i => i.ingredient.toLowerCase().includes(term)) || recipe.tags.some(t => t.toLowerCase().includes(term)) || recipe.parts.some(p => matches(p, term))
}
const filteredRecipes = computed(() => recipes.value.filter(r =>
  (!props.favourites || r.is_favourite) && (!onlyMine.value || r.can_edit) &&
  (!selectedCategory.value || r.category === selectedCategory.value) &&
  selectedTags.value.every(tag => r.tags.some(t => tagKey(t) === tagKey(tag))) && matches(r, searchTerm.value.toLowerCase())))
function clearFilters() { searchTerm.value = ''; selectedCategory.value = ''; selectedTags.value = []; onlyMine.value = false }
async function toggleFavourite(recipe) {
  starBusy.value.add(recipe.id)
  starError.value = ''
  try { const result = await api.setFavourite(recipe.id, !recipe.is_favourite); recipe.is_favourite = result.is_favourite }
  catch (e) { starError.value = e.message }
  finally { starBusy.value.delete(recipe.id) }
}
async function loadRecipes() {
  if (props.favourites && !session.user) { loading.value = false; return }
  loading.value = true
  error.value = ''
  try { recipes.value = await api.getRecipes(props.favourites) } catch (e) { error.value = e.message }
  finally { loading.value = false }
}
onMounted(loadRecipes)
</script>
