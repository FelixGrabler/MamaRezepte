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

      <div v-if="recipe.tags && recipe.tags.length" class="recipe-tags">
        <span v-for="tag in recipe.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>

      <!-- Main recipe ingredients -->
      <div class="ingredients-section">
        <h3>Zutaten{{ childRecipes.length ? ' (Hauptrezept)' : '' }}</h3>
        <ul class="ingredients-list">
          <li v-for="(ingredient, index) in formattedIngredients" :key="`main-ingredient-${index}`">
            {{ ingredient }}
          </li>
        </ul>
      </div>

      <!-- Child recipe ingredients -->
      <div v-if="childRecipes.length" class="child-recipes-container">
        <h3 class="child-recipes-title">Unterrezepte</h3>
        <div v-for="childRecipe in childRecipes" :key="childRecipe.id" class="child-recipe">
          <h4>{{ childRecipe.title }}</h4>
          
          <div class="ingredients-section">
            <h5>Zutaten</h5>
            <ul class="ingredients-list">
              <li v-for="(ingredient, index) in formatIngredients(childRecipe.ingredients)" :key="`child-${childRecipe.id}-ingredient-${index}`">
                {{ ingredient }}
              </li>
            </ul>
          </div>

          <div class="instructions-section">
            <h5>Zubereitung</h5>
            <div class="instructions">{{ childRecipe.instructions }}</div>
          </div>
        </div>
      </div>

      <!-- Main recipe instructions -->
      <div class="instructions-section">
        <h3>Zubereitung{{ childRecipes.length ? ' (Hauptrezept)' : '' }}</h3>
        <div class="instructions">{{ recipe.instructions }}</div>
      </div>

      <div v-if="parentRecipe" class="parent-recipe">
        <p><strong>Teil von:</strong> 
          <button @click="goToRecipe(parentRecipe.id)" class="parent-link">
            {{ parentRecipe.title }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'RecipeDetail',
  props: ['id'],
  data() {
    return {
      recipe: null,
      childRecipes: [],
      parentRecipe: null,
      allRecipes: [],
      loading: true,
      error: null
    }
  },
  computed: {
    formattedIngredients() {
      if (!this.recipe || !this.recipe.ingredients) return []
      return this.formatIngredients(this.recipe.ingredients)
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
        this.error = null
        
        // Load the main recipe
        this.recipe = await apiService.getRecipe(this.id)
        
        // Load all recipes to find relationships
        this.allRecipes = await apiService.getRecipes()
        
        // Find child recipes (recipes that have this recipe as parent)
        this.childRecipes = this.allRecipes.filter(r => 
          r.parent_id && r.parent_id.toString() === this.id.toString()
        )
        
        // Find parent recipe if this recipe has a parent
        this.parentRecipe = null
        if (this.recipe.parent_id) {
          this.parentRecipe = this.allRecipes.find(r => 
            r.id.toString() === this.recipe.parent_id.toString()
          )
        }
        
      } catch (err) {
        this.error = 'Rezept konnte nicht geladen werden: ' + err.message
      } finally {
        this.loading = false
      }
    },
    
    formatIngredients(ingredients) {
      if (!ingredients) return []
      
      return ingredients.map(ingredient => {
        let formatted = ''
        
        if (ingredient.amount) {
          formatted += ingredient.amount
          if (ingredient.unit) {
            formatted += ` ${ingredient.unit}`
          }
          formatted += ' '
        }
        
        formatted += ingredient.ingredient
        
        return formatted
      })
    },
    
    goToRecipe(recipeId) {
      this.$router.push(`/recipe/${recipeId}`)
    },
    
    goBack() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.parent-link {
  color: #667eea;
  cursor: pointer;
  text-decoration: underline;
  background: none;
  border: none;
  padding: 0;
  font: inherit;
}

.parent-link:hover {
  color: #5a6fd8;
}
</style>
