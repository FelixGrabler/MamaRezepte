<template>
  <div>
    <h2>Rezepte Übersicht</h2>
    
    <div class="search-container">
      <input 
        v-model="searchTerm" 
        type="text" 
        placeholder="Rezept suchen..." 
        class="search-input"
      />
    </div>

    <div v-if="loading" class="loading">
      Rezepte werden geladen...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else class="recipe-grid">
      <div 
        v-for="recipe in filteredRecipes" 
        :key="recipe.id"
        class="recipe-card"
        :class="{ 'no-image': !recipe.image_path }"
        @click="goToRecipe(recipe.id)"
      >
        <div v-if="recipe.image_path" class="recipe-image">
          <img :src="`/data/${recipe.image_path}`" :alt="recipe.title" />
        </div>
        <div class="recipe-content">
          <h3 class="recipe-title">{{ recipe.title }}</h3>
          <div v-if="recipe.tags && recipe.tags.length" class="recipe-tags">
            <span v-for="(tag, index) in recipe.tags" :key="`${recipe.id}-tag-${index}`" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !error && filteredRecipes.length === 0 && searchTerm" class="error">
      Keine Rezepte gefunden für "{{ searchTerm }}"
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'RecipeList',
  data() {
    return {
      recipes: [],
      loading: true,
      error: null,
      searchTerm: ''
    }
  },
  computed: {
    filteredRecipes() {
      // Only show recipes that are not sub-recipes (parent_id is null/undefined)
      let parentRecipes = this.recipes.filter(recipe => !recipe.parent_id)
      
      if (!this.searchTerm) {
        return parentRecipes
      }
      const term = this.searchTerm.toLowerCase()
      return parentRecipes.filter(recipe => 
        recipe.title.toLowerCase().includes(term) ||
        recipe.ingredients.some(ingredient => 
          ingredient.ingredient.toLowerCase().includes(term)
        ) ||
        (recipe.tags && recipe.tags.some(tag => 
          tag.toLowerCase().includes(term)
        ))
      )
    }
  },
  async mounted() {
    await this.loadRecipes()
  },
  methods: {
    async loadRecipes() {
      try {
        this.loading = true
        this.recipes = await apiService.getRecipes()
      } catch (err) {
        this.error = 'Rezepte konnten nicht geladen werden: ' + err.message
      } finally {
        this.loading = false
      }
    },
    goToRecipe(id) {
      this.$router.push(`/recipe/${id}`)
    }
  }
}
</script>
