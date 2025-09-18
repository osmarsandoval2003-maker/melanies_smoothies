# Import python package
import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# App title
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on Smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

st.dataframe(pd_df)
st.stop()
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
    st.write("Your selected ingredients:", ingredients_string)
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

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





