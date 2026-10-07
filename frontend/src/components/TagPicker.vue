<template>
  <div class="tag-picker">
    <label for="new-tag">Tags hinzufügen<input id="new-tag" v-model="draft" list="tag-suggestions" maxlength="60" placeholder="Tag auswählen oder neu anlegen" @keydown.enter.prevent="add(draft)" /></label>
    <datalist id="tag-suggestions"><option v-for="tag in suggestions" :key="tag" :value="tag" /></datalist>
    <button type="button" class="secondary-button" :disabled="!draft.trim() || modelValue.length >= 20" @click="add(draft)">Tag hinzufügen</button>
    <div class="recipe-tags selected-tags" aria-label="Zugewiesene Tags">
      <button v-for="tag in modelValue" :key="tag" type="button" class="tag" :aria-label="`Tag ${tag} entfernen`" @click="remove(tag)">{{ tag }} ×</button>
    </div>
    <p class="field-help">Bis zu 20 Tags. Neue Tags werden zusammen mit dem Rezept gespeichert.</p>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { tagKey } from '../services/catalogue'
const props = defineProps({ modelValue: { type: Array, default: () => [] }, suggestions: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])
const draft = ref('')
function add(value) {
  const tag = value.trim()
  if (!tag || props.modelValue.length >= 20) return
  if (!props.modelValue.some(existing => tagKey(existing) === tagKey(tag))) emit('update:modelValue', [...props.modelValue, tag])
  draft.value = ''
}
function remove(tag) { emit('update:modelValue', props.modelValue.filter(value => value !== tag)) }
</script>
