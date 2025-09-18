# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col

# App title and instructions
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

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
    ingredients_string = " ".join(ingredient_list)
    st.write("Your selected ingredients:", ingredients_string)

    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit button
    time_to_insert = st.button("Submit Order")

    # If button is clicked, insert order
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_dt=st.dataframe(data=smoothiefroot_respone.json(),use_container_width=True)

