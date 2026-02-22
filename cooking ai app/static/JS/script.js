const state = {
  recipeLoaded: false,
  currentRecipe: null
};

const heroSection = document.getElementById("heroSection");
const recipeSection = document.getElementById("recipeSection");
const recipeTitle = document.getElementById("recipeTitle");
const ingredientsList = document.getElementById("ingredientsList");
const stepsList = document.getElementById("stepsList");
const answerArea = document.getElementById("answerArea");
const composerForm = document.getElementById("composerForm");
const composerInput = document.getElementById("composerInput");
const submitBtn = document.getElementById("submitBtn");

composerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = composerInput.value.trim();
  if (!text) return;
  
  if (!state.recipeLoaded) {
    // First use: treat input as URL
    await handleUnclutter(text);
  } else {
    // After recipe loads: treat input as a question
    await handleQuestion(text);
  }
});

async function handleUnclutter(url) {
  setLoading(true, "Uncluttering your recipe...");
  try {
    const response = await fetch("http://127.0.0.1:5000/parse-recipe", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url })
    });

    if (!response.ok) {
      throw new Error("Failed to parse recipe.");
    }
    
    const data = await response.json();
    state.currentRecipe = data;
    renderRecipe(data);
    
    // Switch composer to question mode
    composerInput.value = "";
    composerInput.placeholder = "Ask about substitutions, cook time, etc...";
    submitBtn.textContent = "Ask";
  } catch (err) {
    answerArea.textContent = "Could not unclutter that recipe URL. Try another one.";
    console.error(err);
  } finally {
    setLoading(false);
  }
}

async function handleQuestion(question) {
  setLoading(true, "Thinking...");
  try {
    const response = await fetch("http://127.0.0.1:5000/ask-recipe", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question,
        recipe_context: state.currentRecipe
      })
    });

    if (!response.ok) {
      throw new Error("Failed to get answer.");
    }
    
    const data = await response.json();
    answerArea.textContent = data.answer;
    composerInput.value = "";
    
    // Auto-scroll so user can see the new answer
    answerArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (err) {
    answerArea.textContent = "Could not get an answer right now.";
    console.error(err);
  } finally {
    setLoading(false);
  }
}

function renderRecipe(recipe) {
  heroSection.classList.add("hidden");
  recipeSection.classList.remove("hidden");
  recipeTitle.textContent = recipe.title || "Uncluttered Recipe";
  ingredientsList.innerHTML = "";
  
  (recipe.ingredients || []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;

    // Add a click listener for interactivity
    li.addEventListener("click", () => {
      li.classList.toggle("completed");
    });

    ingredientsList.appendChild(li);
  });
  
  stepsList.innerHTML = "";
  (recipe.steps || []).forEach((step) => {
    const li = document.createElement("li");
    li.textContent = step;
    stepsList.appendChild(li);
  });
  
  answerArea.textContent = "Recipe loaded! Feel free to ask any questions below.";
  state.recipeLoaded = true;
  
  // Smoothly glide up to the newly loaded recipe
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setLoading(isLoading, msg = "Loading...") {
  if (isLoading) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Wait";
    if (state.recipeLoaded) {
      answerArea.textContent = msg;
    }
  } else {
    submitBtn.disabled = false;
    submitBtn.textContent = state.recipeLoaded ? "Ask" : "Unclutter";
  }
}