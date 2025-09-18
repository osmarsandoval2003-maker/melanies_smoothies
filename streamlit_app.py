# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# App title and instructions
st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.markdown(f"### 🧃 Your Smoothie will be called: **{name_on_order}**")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Ingredient selection
ingredient_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_list,
    max_selections=5
)

# If ingredients are selected
if ingredient_list:
    ingredients_string = ", ".join(ingredient_list)
    st.write("🍍 Your selected ingredients:", " | ".join([f"🥝 {fruit}" for fruit in ingredient_list]))

    # Show nutrition info for each fruit
    for fruit_chosen in ingredient_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            response = requests.get(f"https://www.smoothiefroot.com/api/fruit/{fruit_chosen}")
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                data = [data]
            df = pd.DataFrame(data)[["name", "id", "carbohydrates", "protein", "fat", "calories", "sugar"]]
            st.dataframe(df, use_container_width=True)
        except requests.exceptions.RequestException:
            st.warning(f"⚠️ {fruit_chosen} is not in the Fruityvice database.")

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button("Submit Order")

    # If button is clicked, insert order
    if time_to_insert:
        if not name_on_order:
            st.error("Please enter a name for your smoothie.")
        else:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")



