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
        v-for="(recipe, index) in filteredRecipes" 
        :key="index"
        class="recipe-card"
        @click="goToRecipe(index)"
      >
        <h3 class="recipe-title">{{ recipe.title }}</h3>
      </div>
    </div>

    <div v-if="!loading && !error && filteredRecipes.length === 0 && searchTerm" class="error">
      Keine Rezepte gefunden für "{{ searchTerm }}"
    </div>
  </div>
</template>

<script>
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
      if (!this.searchTerm) {
        return this.recipes
      }
      const term = this.searchTerm.toLowerCase()
      return this.recipes.filter(recipe => 
        recipe.title.toLowerCase().includes(term) ||
        recipe.ingredients.some(ingredient => 
          ingredient.toLowerCase().includes(term)
        )
      )
    }
  },
  async mounted() {
    try {
      const response = await fetch('/data/recipes.json')
      if (!response.ok) {
        throw new Error('Fehler beim Laden der Rezepte')
      }
      this.recipes = await response.json()
    } catch (err) {
      this.error = 'Rezepte konnten nicht geladen werden: ' + err.message
    } finally {
      this.loading = false
    }
  },
  methods: {
    goToRecipe(index) {
      this.$router.push(`/recipe/${index}`)
    }
  }
}
</script>
