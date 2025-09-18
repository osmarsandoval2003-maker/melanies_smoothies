# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App title
st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on Smoothie
name_on_order = st.text_input("Name on Smoothie:", value="Johnny")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
session = get_active_session()

# Fetch fruit options with SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()
fruit_list = pd_df["FRUIT_NAME"].tolist()

# Ingredient selection
ingredient_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_list,
    default=["Apples", "Blueberries", "Dragon Fruit"],
    max_selections=5
)

# If ingredients are selected
if ingredient_list:
    # Mostrar ingredientes como etiquetas rojas
    st.markdown(" ".join([
        f"<span style='background-color:#ff4b4b;color:white;padding:6px 10px;border-radius:12px;margin-right:6px;'>{fruit}</span>"
        for fruit in ingredient_list
    ]), unsafe_allow_html=True)

    # Mostrar SEARCH_ON y nutrición por fruta
    ingredients_string = ""
    for fruit_chosen in ingredient_list:
        ingredients_string += fruit_chosen + " "

        match = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"]
        if not match.empty:
            search_on = match.iloc[0]
            st.markdown(f"**The search value for {fruit_chosen} is {search_on}.** 👁️")
        else:
            st.warning(f"No SEARCH_ON value found for {fruit_chosen}.")
            search_on = fruit_chosen  # fallback

        # Mostrar sección de nutrición
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                data = [data]
            df = pd.DataFrame(data)
            desired_columns = ["name", "id", "carbohydrates", "protein", "fat", "calories", "sugar"]
            available_columns = [col for col in desired_columns if col in df.columns]
            if available_columns:
                st.dataframe(df[available_columns], use_container_width=True)
            else:
                st.table(pd.DataFrame([{"error": "value", "value": "not found"}]))
        except requests.exceptions.RequestException:
            st.table(pd.DataFrame([{"error": "value", "value": "not found"}]))

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
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

