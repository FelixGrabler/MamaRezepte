// API service for communicating with the backend
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8051";

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  // Recipe endpoints
  async getRecipes() {
    return this.request("/recipes/");
  }

  async getRecipe(id) {
    return this.request(`/recipes/${id}`);
  }

  async createRecipe(recipeData) {
    return this.request("/recipes/", {
      method: "POST",
      body: JSON.stringify(recipeData),
    });
  }

  async deleteRecipe(id) {
    return this.request(`/recipes/${id}`, {
      method: "DELETE",
    });
  }

  // Tag endpoints
  async getTags() {
    return this.request("/tags/");
  }

  async createTag(tagData) {
    return this.request("/tags/", {
      method: "POST",
      body: JSON.stringify(tagData),
    });
  }

  async deleteTag(id) {
    return this.request(`/tags/${id}`, {
      method: "DELETE",
    });
  }

  async addTagToRecipe(recipeId, tagId) {
    return this.request("/tags/recipe-tags", {
      method: "POST",
      body: JSON.stringify({ recipe_id: recipeId, tag_id: tagId }),
    });
  }

  async removeTagFromRecipe(recipeId, tagId) {
    return this.request("/tags/recipe-tags", {
      method: "DELETE",
      body: JSON.stringify({ recipe_id: recipeId, tag_id: tagId }),
    });
  }
}

export default new ApiService();
