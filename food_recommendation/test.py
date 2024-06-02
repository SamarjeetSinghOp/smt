from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

app = Flask(__name__)

# Function to get macros data from the website
def get_macros_data(json_input):
    url = "https://www.calculator.net/macro-calculator.html"
    
    params = {
        "ctype": "metric",
        "cage": json_input["Age"],
        "csex": json_input["Sex"],
        "cheightmeter": json_input["Height"],
        "ckg": json_input["Weight"],
        "cactivity": json_input["Activity"],
        "cgoal": json_input["Goal"],
        "printit": 0,
        "x": 121,
        "y": 28
    }
    
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    macros = {}
    
    labels = soup.find_all('td', {'class': 'arrow_box'})
    values = soup.find_all('td', {'class': 'result_box'})
    for label, value in zip(labels, values):
        temp_lab = label.div.text.strip()
        temp_val = value.text.replace('<', '').replace(':', '').strip().split(" ")
        macros[temp_lab + " (" + temp_val[1] + ")"] = temp_val[0]
    
    macros["Preference"] = json_input["Preference"]
    return [macros]

# Function to select food items based on required nutrient levels and user preference
def select_food_item(df, required_nutrients, meal):
    preference = required_nutrients["Preference"]
    meal_df = df[df['Meal'] == meal]
    if preference == 'veg':
        meal_df = meal_df[meal_df['Category'] == 'Veg']
    else:
        meal_df = meal_df[(meal_df['Category'] == 'Non-Veg') | (meal_df['Category'] == 'Veg')]
    item = meal_df.sample(n=1)
    return item.iloc[0].to_dict()

# Function to generate dietary plan for a day
def generate_daily_diet(df, required_nutrients):
    daily_diet_plan = {
        "Breakfast": select_food_item(df, required_nutrients, 'Breakfast'),
        "Lunch": select_food_item(df, required_nutrients, 'Lunch'),
        "Dinner": select_food_item(df, required_nutrients, 'Dinner')
    }
    return daily_diet_plan

# Function to generate weekly dietary plan
def generate_weekly_diet_plan(df, required_nutrients):
    weekly_diet_plan = {}
    for day in range(1, 8):
        daily_diet = generate_daily_diet(df, required_nutrients)
        weekly_diet_plan[f"Day {day}"] = daily_diet
    return weekly_diet_plan

# Load the Excel data
df = pd.read_excel("food_data.xlsx")

@app.route('/generate_diet_plan', methods=['POST'])
def generate_diet_plan():
    try:
        # Parse input JSON
        data = request.get_json()
        
        # Get macros data from the scrapped website
        macros_data = get_macros_data(data)
        
        # Iterate over each user's nutrient requirements and generate a weekly diet plan
        for user_macros in macros_data:
            required_nutrients = {
                "Protein(g)": user_macros["Protein (grams/day)"],  # Example values, replace with actual values as needed
                "Total lipid (fat)(g)": user_macros["Fat (grams/day)"],
                "Carbohydrate by difference(g)": user_macros["Carbs (grams/day)"],
                "Energy(kcal)": user_macros["Food Energy (Calories/dayor)"],
                "Sugars total including NLEA(g)": user_macros["Sugar (grams/day)"],
                "Preference": user_macros["Preference"]
            }
            
            # Generate weekly dietary plan based on user preference
            weekly_diet_plan = generate_weekly_diet_plan(df, required_nutrients)
            
            # Convert the dietary plan to JSON
            diet_plan_json = json.dumps(weekly_diet_plan, indent=4)
            
            return jsonify(weekly_diet_plan), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=1373, debug=True)

# sex will have m for male and f female

# preference will have veg and non-veg(others)

# height is in centimeter (cm)

# weight will be in kilogram (kg) 

# activity will have 
# 1 for Basal Metabolic Rate (BMR)
# 1.2 for Sedentary: little or no exercise
# 1.375 for Light: exercise 1-3 times/week
# 1.465 for Moderate: exercise 4-5 times/week
# 1.55 for Active: daily exercise or intense exercise 3-4 times/week
# 1.725 for Very Active: intense exercise 6-7 times/week
# 1.9 for Extra Active: very intense exercise daily, or physical job
#
# add below info while giving option to user
# [ 
#     Exercise: 15-30 minutes of elevated heart rate activity.
#     Intense exercise: 45-120 minutes of elevated heart rate activity.
#     Very intense exercise: 2+ hours of elevated heart rate activity.
#  ]

#goal will have
# m for Maintain weight
# l for Mild weight loss of 0.5 lb (0.25 kg) per week
# l1 for Weight loss of 1 lb (0.5 kg) per week
# l2 for Extreme weight loss of 2 lb (1 kg) per week
# g for Mild weight gain of 0.5 lb (0.25 kg) per week
# g1 for Weight gain of 1 lb (0.5 kg) per week
# g2 for Extreme weight gain of 2 lb (1 kg) per week

# sample input
# {
#     "Height": 170,
#     "Weight": 70,
#     "Preference": "veg",
#     "Age": 21,
#     "Activity": 1.725,
#     "Sex": "m",
#     "Goal": "g2"
# }

# sample url
# url : http://127.0.0.1:1373/generate_diet_plan
