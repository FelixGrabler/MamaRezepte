<template>
  <div>
    <button @click="goBack" class="back-button">
      ← Zurück zur Übersicht
    </button>

    <div v-if="loading" class="loading">
      Rezept wird geladen...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="recipe" class="recipe-detail">
      <h1>{{ recipe.title }}</h1>

      <div v-if="recipe.image_path" class="recipe-detail-image">
        <img :src="`/data/${recipe.image_path}`" :alt="recipe.title" />
      </div>

      <div class="ingredients-section">
        <h3>Zutaten</h3>
        <ul class="ingredients-list">
          <li v-for="ingredient in formattedIngredients" :key="ingredient">
            {{ ingredient }}
          </li>
        </ul>
      </div>

      <div class="instructions-section">
        <h3>Zubereitung</h3>
        <div class="instructions">{{ recipe.instructions }}</div>
      </div>

      <div v-if="recipe.parent_recipe" class="parent-recipe">
        <p><strong>Basis-Rezept:</strong> {{ recipe.parent_recipe }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecipeDetail',
  props: ['id'],
  data() {
    return {
      recipe: null,
      recipes: [],
      loading: true,
      error: null
    }
  },
  computed: {
    formattedIngredients() {
      if (!this.recipe || !this.recipe.ingredients) return []
      
      return this.recipe.ingredients.map(ingredient => {
        // Format ingredients by replacing underscores with spaces and cleaning up
        return ingredient
          .replace(/_/g, ' ')
          .replace(/\s+/g, ' ')
          .trim()
      })
    }
  },
  async mounted() {
    await this.loadRecipe()
  },
  watch: {
    id() {
      this.loadRecipe()
    }
  },
  methods: {
    async loadRecipe() {
      try {
        this.loading = true
        const response = await fetch('/data/recipes.json')
        if (!response.ok) {
          throw new Error('Fehler beim Laden der Rezepte')
        }
        this.recipes = await response.json()
        
        const recipeIndex = parseInt(this.id)
        if (recipeIndex >= 0 && recipeIndex < this.recipes.length) {
          this.recipe = this.recipes[recipeIndex]
        } else {
          throw new Error('Rezept nicht gefunden')
        }
      } catch (err) {
        this.error = 'Rezept konnte nicht geladen werden: ' + err.message
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push('/')
    }
  }
}
</script>
