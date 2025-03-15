import streamlit as st
import os
# Import functions from the recipe.py module
from recipe import generate_recipe, get_dish_details, save_recipe, MODEL_NAME

# Set Page Configuration
st.set_page_config(
    page_title="SmartChef AI - Recipe Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App Header with Custom Styling
st.title("👨‍🍳 SmartChef AI - Your Personal Recipe Assistant")
st.markdown("""
    <style>
    .recipe-header {
        color: #FF6B6B;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown('<p class="recipe-header">Get custom recipes based on your ingredients and preferences. AI-powered cooking made easy! 🍽️🔥</p>', unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=SmartChef", width=150)
    st.header("Navigation")
    option = st.radio("Choose an Option:", ["🍲 Create a New Recipe", "🔍 Find a Dish Recipe"])
    
    st.markdown("---")
    st.markdown(f"🤖 Using AI Model: **{MODEL_NAME}**")
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("For best results, be specific with your ingredients and preferences!")

# Recipe Generation Form
if option == "🍲 Create a New Recipe":
    st.header("Create Your Perfect Recipe")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Enter Recipe Preferences")
        ingredients = st.text_area("🥕 Ingredients (comma-separated)", "Tomato, Onion, Garlic, Chicken")
        
        col1a, col1b = st.columns(2)
        with col1a:
            diet = st.selectbox("🥗 Dietary Preference", ["None", "Vegan", "Vegetarian", "Keto", "Gluten-Free", "Low-Carb", "Paleo"])
            meal_type = st.selectbox("🍽️ Meal Type", ["Dinner", "Breakfast", "Lunch", "Snack", "Dessert", "Appetizer"])
        
        with col1b:
            cooking_time = st.slider("⏳ Cooking Time (minutes)", 5, 120, 30)
            servings = st.number_input("👨‍👩‍👧‍👦 Servings", min_value=1, max_value=10, value=2)
        
        generate_button = st.button("🚀 Generate Recipe", use_container_width=True)
    
    with col2:
        st.subheader("🧪 Recipe Complexity")
        complexity = st.select_slider(
            "Select complexity level",
            options=["Simple", "Moderate", "Gourmet"],
            value="Moderate"
        )
        st.caption("This affects the sophistication of techniques and ingredients in your recipe.")
        
        st.markdown("---")
        st.subheader("📊 Nutrition Focus")
        nutrition_focus = st.multiselect(
            "Select nutrition priorities",
            ["High Protein", "Low Fat", "Low Carb", "High Fiber"],
            []
        )
    
    # Generate Recipe
    if generate_button:
        with st.spinner("👨‍🍳 Cooking up your AI-powered recipe..."):
            nutrition_str = ", ".join(nutrition_focus) if nutrition_focus else "Balanced"
            recipe_input = f"{ingredients} with {complexity} complexity and focus on {nutrition_str}"
            recipe = generate_recipe(recipe_input, diet, meal_type, cooking_time, servings)
        
        st.success("Recipe created successfully!")
        st.subheader("✨ Your AI-Generated Recipe")
        
        # Display Recipe
        recipe_container = st.container()
        with recipe_container:
            st.markdown(recipe)
        
        # Save Recipe Options
        st.subheader("💾 Save Your Recipe")
        col_save1, col_save2, col_save3 = st.columns(3)
        
        with col_save1:
            file_name = st.text_input("📁 File name", "my_recipe")
        
        with col_save2:
            file_format = st.selectbox("📂 Format", ["TXT", "DOCX", "PDF"])
        
        with col_save3:
            st.write(" ")
            st.write(" ")
            if st.button("💾 Save", use_container_width=True):
                try:
                    saved_file = save_recipe(recipe, file_name, file_format.lower())
                    st.success(f"✅ Recipe saved as `{saved_file}`")
                    with open(saved_file, "rb") as file:
                        st.download_button(
                            label="📥 Download Recipe",
                            data=file,
                            file_name=os.path.basename(saved_file),
                            mime="application/octet-stream"
                        )
                except Exception as e:
                    st.error(f"Error saving recipe: {str(e)}")

# Dish Lookup Feature
if option == "🔍 Find a Dish Recipe":
    st.header("Discover Classic Recipes")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🍽️ Enter a Dish Name")
        dish_name = st.text_input("🔎 What dish would you like to cook?", "Pasta Carbonara")
        get_recipe_button = st.button("📌 Get Recipe", use_container_width=True)
    
    with col2:
        st.subheader("🌍 Cuisine Style")
        cuisine = st.selectbox(
            "Filter by cuisine (optional)",
            ["Any", "Italian", "Chinese", "Indian", "Mexican", "French", "Japanese", "Thai", "Mediterranean"]
        )
        st.caption("This helps refine the recipe style.")
    
    # Get Dish Details
    if get_recipe_button:
        search_term = dish_name
        if cuisine != "Any":
            search_term = f"{cuisine} {dish_name}"
            
        with st.spinner(f"🔍 Finding the best {search_term} recipe..."):
            dish_details = get_dish_details(search_term)
        
        st.success("Recipe found!")
        st.subheader(f"✨ Recipe for {dish_name}")
        
        # Display Recipe
        recipe_container = st.container()
        with recipe_container:
            st.markdown(dish_details)
        
        # Save Recipe Options
        st.subheader("💾 Save This Recipe")
        col_save1, col_save2, col_save3 = st.columns(3)
        
        with col_save1:
            file_name = st.text_input("📁 File name", dish_name.replace(" ", "_").lower())
        
        with col_save2:
            file_format = st.selectbox("📂 Format", ["TXT", "DOCX", "PDF"])
        
        with col_save3:
            st.write(" ")
            st.write(" ")
            if st.button("💾 Save", use_container_width=True):
                try:
                    saved_file = save_recipe(dish_details, file_name, file_format.lower())
                    st.success(f"✅ Recipe saved as `{saved_file}`")
                    with open(saved_file, "rb") as file:
                        st.download_button(
                            label="📥 Download Recipe",
                            data=file,
                            file_name=os.path.basename(saved_file),
                            mime="application/octet-stream"
                        )
                except Exception as e:
                    st.error(f"Error saving recipe: {str(e)}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🚀 Built with ❤️ using Streamlit")
with col2:
    st.markdown("🤖 Powered by AI")
with col3:
    st.markdown("👨‍🍳 Share your creations!")