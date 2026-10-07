<template>
  <section class="form-panel">
    <h1>{{ id ? 'Rezept bearbeiten' : 'Neues Rezept' }}</h1>
    <p v-if="!session.user">Bitte <router-link :to="{ path: '/login', query: { next: $route.fullPath } }">anmelden</router-link>, um ein Rezept zu erstellen.</p>
    <p v-else-if="loading" class="loading">Rezept wird geladen…</p>
    <p v-else-if="loadError" class="error" role="alert">{{ loadError }}</p>
    <form v-else @submit.prevent="save">
      <fieldset :disabled="busy">
        <label>Rezeptname<input v-model="recipe.title" required maxlength="200" /></label>
        <label class="checkbox-label"><input v-model="recipe.is_public" type="checkbox" /> Öffentlich sichtbar</label>
        <p class="field-help">{{ recipe.is_public ? 'Alle können dieses Rezept und seine Teile sehen.' : 'Nur du kannst dieses Rezept, seine Teile und sein Bild sehen.' }}</p>
        <div class="recipe-fields">
          <label>Kategorie<select v-model="recipe.category" required><option v-for="category in categories" :key="category">{{ category }}</option></select></label>
          <label>Portionen des Rezepts<input v-model.number="recipe.servings" type="number" required min="1" max="1000" step="1" /></label>
        </div>
        <p class="field-help">Die Zutatenmengen unten gelten für diese Portionenzahl.</p>
        <TagPicker v-model="recipe.tags" :suggestions="tagSuggestions" />
        <label>Foto<input type="file" accept="image/jpeg,image/png,image/webp" @change="chooseImage" /></label>
        <p class="field-help">JPEG, PNG oder WebP, bis 20 MB. Bilder werden automatisch verkleinert.</p>
        <img v-if="preview || currentImage" :src="preview || currentImage" alt="Rezeptfoto" class="editor-preview" />
        <label v-if="currentImage && !image" class="checkbox-label"><input v-model="removeImage" type="checkbox" /> Vorhandenes Foto entfernen</label>
        <section v-for="(part, sectionIndex) in sections" :key="sectionIndex" class="editor-section">
          <div class="page-heading">
            <h2>{{ sectionIndex === 0 ? 'Hauptrezept' : `Teil ${sectionIndex}` }}</h2>
            <div v-if="sectionIndex > 0" class="actions">
              <button type="button" :disabled="sectionIndex === 1" @click="movePart(sectionIndex - 1, -1)" aria-label="Teil nach oben verschieben">↑</button>
              <button type="button" :disabled="sectionIndex === recipe.parts.length" @click="movePart(sectionIndex - 1, 1)" aria-label="Teil nach unten verschieben">↓</button>
              <button type="button" @click="recipe.parts.splice(sectionIndex - 1, 1)">Teil entfernen</button>
            </div>
          </div>
          <label v-if="sectionIndex > 0">Name des Teils<input v-model="part.title" required maxlength="200" placeholder="z. B. Teig" /></label>
          <h3>Zutaten</h3>
          <div v-for="(ingredient, i) in part.ingredients" :key="i" class="ingredient-row">
            <label>Menge<input v-model="ingredient.amount" type="number" min="0" step="any" placeholder="optional" /></label>
            <label>Einheit<input v-model="ingredient.unit" maxlength="40" placeholder="g, EL…" /></label>
            <label>Zutat<input v-model="ingredient.ingredient" required maxlength="250" placeholder="Zutat" /></label>
            <button type="button" @click="part.ingredients.splice(i, 1)" aria-label="Zutat entfernen">×</button>
          </div>
          <button type="button" class="secondary-button" :disabled="part.ingredients.length >= 200" @click="part.ingredients.push({amount: '', unit: '', ingredient: ''})">+ Zutat</button>
          <label>Zubereitung<textarea v-model="part.instructions" rows="6" maxlength="30000" /></label>
        </section>
        <button type="button" class="secondary-button" :disabled="recipe.parts.length >= 30" @click="recipe.parts.push(blankPart())">+ Rezeptteil hinzufügen</button>
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <p v-if="contentSaved && error" class="field-help">Der Rezepttext ist gespeichert. Du kannst das Foto erneut auswählen und nochmals speichern.</p>
        <div class="actions form-actions">
          <button type="submit" class="primary-button">{{ busy ? 'Wird gespeichert…' : 'Rezept speichern' }}</button>
          <router-link class="secondary-button" :to="savedId ? `/recipe/${savedId}` : '/'">Abbrechen</router-link>
        </div>
      </fieldset>
    </form>
  </section>
</template>
<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import api, { session } from '../services/api'
import { categories } from '../services/catalogue'
import TagPicker from './TagPicker.vue'
const props = defineProps(['id'])
const router = useRouter()
function blankPart() { return {title: '', instructions: '', ingredients: []} }
const recipe = ref({ ...blankPart(), is_public: true, category: 'sonstiges', servings: 4, tags: [], parts: [] })
const tagSuggestions = ref([]), loading = ref(false), loadError = ref(''), error = ref(''), busy = ref(false)
const contentSaved = ref(false)
const savedId = ref(props.id || null), image = ref(null), preview = ref(''), currentImage = ref(''), removeImage = ref(false)
const sections = computed(() => [recipe.value, ...recipe.value.parts])
function chooseImage(event) {
  error.value = ''
  const file = event.target.files[0]
  if (preview.value) URL.revokeObjectURL(preview.value)
  image.value = null
  preview.value = ''
  if (!file) return
  if (file.size > 20 * 1024 * 1024) {
    error.value = 'Bilder dürfen höchstens 20 MB groß sein.'
    event.target.value = ''
    return
  }
  image.value = file
  preview.value = URL.createObjectURL(file)
}
function movePart(index, delta) {
  const parts = recipe.value.parts
  ;[parts[index], parts[index + delta]] = [parts[index + delta], parts[index]]
}
function content(part) {
  return { title: part.title, instructions: part.instructions,
    ingredients: part.ingredients.map(i => ({ ingredient: i.ingredient,
      amount: i.amount === '' || i.amount == null ? null : Number(i.amount), unit: i.unit || null })) }
}
async function save() {
  busy.value = true
  error.value = ''
  contentSaved.value = false
  try {
    const body = { ...content(recipe.value), is_public: recipe.value.is_public,
      category: recipe.value.category, servings: recipe.value.servings, tags: recipe.value.tags,
      parts: recipe.value.parts.map(part => ({ ...content(part), ...(part.id ? { id: part.id } : {}) })) }
    const saved = savedId.value ? await api.updateRecipe(savedId.value, body) : await api.createRecipe(body)
    savedId.value = saved.id
    contentSaved.value = true
    recipe.value.parts.forEach((part, index) => { part.id = saved.parts[index].id })
    if (image.value) await api.uploadImage(saved.id, image.value)
    else if (removeImage.value) await api.removeImage(saved.id)
    router.push(`/recipe/${saved.id}`)
  } catch (e) { error.value = e.message }
  finally { busy.value = false }
}
onMounted(async () => {
  if (!session.user) return
  loading.value = true
  try {
    tagSuggestions.value = (await api.getTags()).map(tag => tag.name)
    if (!props.id) return
    const source = await api.getRecipe(props.id)
    if (!source.can_edit || source.parent_id) throw new Error('Dieses Rezept kann nicht bearbeitet werden.')
    recipe.value = { ...content(source), is_public: source.is_public, category: source.category,
      servings: source.servings, tags: source.tags, parts: source.parts.map(part => ({ ...content(part), id: part.id })) }
    currentImage.value = api.imageUrl(source)
  } catch (e) { loadError.value = e.message }
  finally { loading.value = false }
})
onBeforeUnmount(() => { if (preview.value) URL.revokeObjectURL(preview.value) })
</script>
