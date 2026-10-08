<template>
  <div>
    <div class="page-heading"><h2>{{ favourites ? 'Favouriten' : 'Rezepte Übersicht' }}</h2><router-link v-if="session.user" class="primary-button" to="/new">+ Neues Rezept</router-link></div>
    <p v-if="favourites && !session.user">Bitte <router-link to="/login?next=/favourites">anmelden</router-link>, um deine Favouriten zu sehen.</p>
    <template v-else>
      <div class="recipe-browser">
        <aside class="recipe-filters" aria-label="Rezepte filtern">
          <label class="sr-only" for="recipe-search">Rezept oder Zutat suchen</label>
          <input id="recipe-search" v-model="searchTerm" placeholder="Rezept oder Zutat suchen…" class="search-input" />
          <div class="filters">
            <label>Kategorie<select v-model="selectedCategory"><option value="">Alle Kategorien</option><option v-for="category in categories" :key="category">{{ category }}</option></select></label>
            <label v-if="session.user" class="checkbox-label"><input type="checkbox" v-model="onlyMine" /> Nur meine Rezepte</label>
          </div>
          <fieldset v-if="availableTags.length" class="tag-filters">
            <legend>Tags</legend>
            <button v-for="tag in availableTags" :key="tag" type="button" class="filter-tag" :class="{ selected: tagState(tag) === 'included', excluded: tagState(tag) === 'excluded' }" :aria-label="tag" :aria-pressed="tagState(tag) !== 'neutral'" :aria-description="tagDescription(tag)" :title="tagDescription(tag)" @click="cycleTag(tag)">
              <span class="filter-tag-state" aria-hidden="true">{{ tagState(tag) === 'included' ? '✓' : tagState(tag) === 'excluded' ? '−' : '+' }}</span><span class="filter-tag-name">{{ tag }}</span>
            </button>
            <p class="field-help">Einmal: einschließen · zweimal: ausschließen · dreimal: zurücksetzen.</p>
            <p v-if="selectedTags.length > 1" class="field-help">Rezepte müssen alle ausgewählten Tags enthalten.</p>
          </fieldset>
          <button v-if="searchTerm || selectedCategory || selectedTags.length || excludedTags.length || onlyMine" class="secondary-button" @click="clearFilters">Filter zurücksetzen</button>
        </aside>
        <div class="recipe-results">
          <div v-if="loading" class="loading">Rezepte werden geladen…</div>
          <div v-else-if="error" class="error" role="alert">{{ error }} <button @click="loadRecipes">Erneut versuchen</button></div>
          <p v-if="starError" class="error" role="alert">{{ starError }}</p>
          <div v-if="!loading && !error" class="recipe-grid">
            <article v-for="recipe in filteredRecipes" :key="recipe.id" class="recipe-card" :class="{ 'no-image': !recipe.image_path }">
              <router-link :to="`/recipe/${recipe.id}`" class="recipe-card-link">
                <div v-if="recipe.image_path" class="recipe-image"><img :src="api.imageUrl(recipe)" :alt="recipe.title" loading="lazy" /></div>
                <div class="recipe-content">
                  <h3 class="recipe-title">{{ recipe.title }}</h3>
                  <span v-if="!recipe.is_public" class="privacy-badge">🔒 Privat</span>
                </div>
              </router-link>
              <FavouriteStar v-if="session.user" class="card-star" :starred="recipe.is_favourite" :label="`${recipe.title}: ${recipe.is_favourite ? 'Aus Favouriten entfernen' : 'Zu Favouriten hinzufügen'}`" :busy="starBusy.has(recipe.id)" @toggle="toggleFavourite(recipe)" />
            </article>
          </div>
          <p v-if="!loading && !error && !filteredRecipes.length" class="empty-state">{{ favourites && !recipes.length ? 'Noch keine Favouriten. Markiere ein Rezept mit einem Stern.' : 'Keine passenden Rezepte gefunden.' }}</p>
        </div>
      </div>
    </template>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import FavouriteStar from './FavouriteStar.vue'
import { useRoute } from 'vue-router'
import api, { session } from '../services/api'
import { categories, tagKey } from '../services/catalogue'
const props = defineProps({ favourites: { type: Boolean, default: false } })
const route = useRoute()
const recipes = ref([]), loading = ref(true), error = ref(''), starError = ref(''), starBusy = ref(new Set())
const searchTerm = ref(''), onlyMine = ref(false)
const selectedCategory = ref(categories.includes(route.query.category) ? route.query.category : '')
const selectedTags = ref(Array.isArray(route.query.tag) ? route.query.tag : route.query.tag ? [route.query.tag] : [])
const excludedTags = ref([])
function hasTag(tags, tag) { return tags.some(t => tagKey(t) === tagKey(tag)) }
function tagState(tag) { return hasTag(selectedTags.value, tag) ? 'included' : hasTag(excludedTags.value, tag) ? 'excluded' : 'neutral' }
function tagDescription(tag) {
  return { neutral: 'Neutral. Klicken zum Einschließen.', included: 'Eingeschlossen. Klicken zum Ausschließen.', excluded: 'Ausgeschlossen. Klicken zum Zurücksetzen.' }[tagState(tag)]
}
function cycleTag(tag) {
  const state = tagState(tag)
  selectedTags.value = selectedTags.value.filter(t => tagKey(t) !== tagKey(tag))
  excludedTags.value = excludedTags.value.filter(t => tagKey(t) !== tagKey(tag))
  if (state === 'neutral') selectedTags.value.push(tag)
  if (state === 'included') excludedTags.value.push(tag)
}
const availableTags = computed(() => [...new Map(recipes.value.flatMap(recipe => recipe.tags).map(tag => [tagKey(tag), tag])).values()].sort((a, b) => a.localeCompare(b, 'de-AT')))
function matches(recipe, term) {
  return recipe.title.toLowerCase().includes(term) || recipe.ingredients.some(i => i.ingredient.toLowerCase().includes(term)) || recipe.tags.some(t => t.toLowerCase().includes(term)) || recipe.parts.some(p => matches(p, term))
}
const filteredRecipes = computed(() => recipes.value.filter(r =>
  (!props.favourites || r.is_favourite) && (!onlyMine.value || r.can_edit) &&
  (!selectedCategory.value || r.category === selectedCategory.value) &&
  selectedTags.value.every(tag => hasTag(r.tags, tag)) &&
  !excludedTags.value.some(tag => hasTag(r.tags, tag)) && matches(r, searchTerm.value.toLowerCase())))
function clearFilters() { searchTerm.value = ''; selectedCategory.value = ''; selectedTags.value = []; excludedTags.value = []; onlyMine.value = false }
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
