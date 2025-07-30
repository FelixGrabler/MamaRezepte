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

      <!-- All ingredients grouped at the top -->
      <div class="all-ingredients-section">
        <h2>Zutaten</h2>
        
        <!-- Main recipe ingredients -->
        <div class="ingredient-group">
          <h3>{{ childRecipes.length ? recipe.title + ' (Hauptrezept)' : recipe.title }}</h3>
          <ul class="ingredients-list">
            <li v-for="(ingredient, index) in formattedIngredients" :key="`main-ingredient-${index}`">
              {{ ingredient }}
            </li>
          </ul>
        </div>

        <!-- Child recipe ingredients -->
        <div v-for="childRecipe in childRecipes" :key="`ingredients-${childRecipe.id}`" class="ingredient-group">
          <h3>{{ childRecipe.title }}</h3>
          <ul class="ingredients-list">
            <li v-for="(ingredient, index) in formatIngredients(childRecipe.ingredients)" :key="`child-${childRecipe.id}-ingredient-${index}`">
              {{ ingredient }}
            </li>
          </ul>
        </div>
      </div>

      <!-- All instructions grouped at the bottom -->
      <div class="all-instructions-section">
        <h2>Zubereitung</h2>
        
        <!-- Child recipe instructions first -->
        <div v-for="childRecipe in childRecipes" :key="`instructions-${childRecipe.id}`" class="instruction-group">
          <h3>{{ childRecipe.title }}</h3>
          <div class="instructions">{{ childRecipe.instructions }}</div>
        </div>

        <!-- Main recipe instructions -->
        <div class="instruction-group">
          <h3>{{ childRecipes.length ? recipe.title + ' (Hauptrezept)' : recipe.title }}</h3>
          <div class="instructions">{{ recipe.instructions }}</div>
        </div>
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
.all-ingredients-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.all-instructions-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #f1f3f4;
  border-radius: 8px;
  border-left: 4px solid #28a745;
}

.ingredient-group {
  margin-bottom: 1.5rem;
}

.ingredient-group:last-child {
  margin-bottom: 0;
}

.instruction-group {
  margin-bottom: 2rem;
}

.instruction-group:last-child {
  margin-bottom: 0;
}

.ingredient-group h3,
.instruction-group h3 {
  color: #333;
  margin-bottom: 0.75rem;
  font-size: 1.2rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.all-ingredients-section h2,
.all-instructions-section h2 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  text-align: center;
  font-weight: bold;
}

.ingredients-list {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

.ingredients-list li {
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.instructions {
  line-height: 1.6;
  white-space: pre-wrap;
  background-color: white;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

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
