# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App title
st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on Smoothie
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.markdown(f"**The name on your Smoothie will be:** `{name_on_order}`")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options with SEARCH_ON column
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)
pd_df = my_dataframe.to_pandas()
fruit_list = pd_df["FRUIT_NAME"].tolist()

# Ingredient selection
ingredient_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_list,
    max_selections=5
)

# If ingredients are selected
if ingredient_list:
    ingredients_string = ", ".join(ingredient_list)
    st.markdown("**Your selected ingredients:**")
    st.markdown(" ".join([
        f"<span style='background-color:#ff4b4b;color:white;padding:4px 8px;border-radius:8px;margin-right:4px;'>{fruit}</span>"
        for fruit in ingredient_list
    ]), unsafe_allow_html=True)

    # Show SEARCH_ON value for each fruit
    for fruit_chosen in ingredient_list:
        match = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"]
        if not match.empty:
            search_on = match.iloc[0]
            st.write(f"The search value for `{fruit_chosen}` is: `{search_on}`")
        else:
            st.warning(f"No SEARCH_ON value found for {fruit_chosen}.")

    # Show nutrition info for Watermelon
    st.subheader("Watermelon Nutrition Information")
    try:
        response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            data = [data]
        df = pd.DataFrame(data)[["name", "id", "carbohydrates", "protein", "fat", "calories", "sugar"]]
        st.dataframe(df, use_container_width=True)
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ Could not retrieve Watermelon data: {e}")

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

