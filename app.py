import streamlit as st
import google.generativeai as genai
import math
from fpdf import FPDF
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API using the correct environment variable
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = "light"
if 'fitness_plan_generated' not in st.session_state:
    st.session_state.fitness_plan_generated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = ""
if 'workout_plan' not in st.session_state:
    st.session_state.workout_plan = ""

def change_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def ideal_weight_range(height_cm):
    height_m = height_cm / 100
    return max(18.5 * (height_m ** 2), 20), min(24.9 * (height_m ** 2), 200)

def calculate_bmr(gender, weight, height, age):
    if gender == "Male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender == "Female":
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        return (88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age) +
                447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)) / 2

def calculate_daily_calorie_needs(bmr, activity_level, goal):
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9
    }
    calorie_needs = bmr * activity_multipliers[activity_level]
    if goal == "Weight Loss":
        calorie_needs -= 500
    elif goal == "Muscle Gain":
        calorie_needs += 300
    return int(calorie_needs)

def get_gemini_response(input_prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-exp-0801")
        response = model.generate_content([input_prompt])

        if response.parts:
            return response.parts[0].text
        else:
            return "I apologize, but I couldn't generate a response at this time. Please try again later."
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "I'm sorry, but there was an error generating a response. Please try again later."

def generate_meal_plan(calorie_goal, restrictions=""):
    prompt = f"""
    Generate a sample 7-day meal plan for a person with a daily calorie goal of {calorie_goal} calories.
    The meal plan should include breakfast, lunch, dinner, and two snacks per day.
    Dietary restrictions: {restrictions}
    Provide the meal plan in a clear and organized format, using bullet points for each day.
    """
    return get_gemini_response(prompt)

def generate_workout_plan(goal, days, duration):
    prompt = f"""
    Create a sample weekly workout plan for someone aiming to {goal},
    who wants to work out {days} days a week, with each workout lasting
    around {duration} minutes.
    Include a variety of exercises targeting different muscle groups.
    Provide clear instructions for each exercise and day.
    """
    return get_gemini_response(prompt)

def cm_to_feet_inches(cm):
    inches = cm / 2.54
    feet, inches = divmod(inches, 12)
    return f"{int(feet)}'{round(inches, 1)}\""

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download file</a>'

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'FitTrack Pro - Your Personalized Fitness Plan', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def export_as_pdf(user_data, meal_plan, workout_plan):
    pdf = PDF()
    pdf.add_page()

    # User Information
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Personal Information", 0, 1)
    pdf.set_font("Arial", '', 10)
    for key, value in user_data.items():
        pdf.cell(0, 8, f"{key}: {value}", 0, 1)
    pdf.ln(5)

    # Meal Plan
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "7-Day Meal Plan", 0, 1)
    pdf.set_font("Arial", '', 10)

    days = meal_plan.split("**Day")
    for day in days[1:]:  # Skip the first empty split
        day_header = day.split(':')[0].strip()
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"Day {day_header}", 0, 1)
        pdf.set_font("Arial", '', 10)

        meals = day.split("*")[1:]  # Skip the day header
        for meal in meals:
            meal_content = meal.strip().replace("**", "").replace("*", "")
            pdf.multi_cell(0, 5, meal_content)
        pdf.ln(5)

    # Workout Plan
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Weekly Workout Plan", 0, 1)
    pdf.set_font("Arial", '', 10)

    sections = workout_plan.split("**")
    for section in sections[1:]:  # Skip the first empty split
        section_header = section.split('\n')[0].strip()
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, section_header, 0, 1)
        pdf.set_font("Arial", '', 10)
        section_content = '\n'.join(section.split('\n')[1:]).strip().replace("**", "").replace("*", "")
        pdf.multi_cell(0, 5, section_content)
        pdf.ln(5)

    return pdf.output(dest="S").encode("latin-1")

# Set page config
st.set_page_config(page_title="FitTrack Pro", page_icon="💪", layout="wide")

# Custom CSS for themes
theme_css = {
    "light": """
        <style>
            .reportview-container { background: #f0f2f6; color: #262730; }
            .big-font { font-size: 30px !important; font-weight: bold; color: #4F8BF9; }
            .stTextInput > div > div > input { color: #4F8BF9; }
        </style>
    """,
    "dark": """
        <style>
            .reportview-container { background: #262730; color: #fafafa; }
            .big-font { font-size: 30px !important; font-weight: bold; color: #4F8BF9; }
            .stTextInput > div > div > input { color: #4F8BF9; }
        </style>
    """
}

st.markdown(theme_css[st.session_state.theme], unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align: center; color: #4F8BF9;'>🏋️‍♂️ FitTrack Pro 🏃‍♀️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your advanced personal fitness companion</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.button("Toggle Theme", on_click=change_theme)
    st.header("Your Information")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=120, value=30)
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    st.write(f"Height in feet: {cm_to_feet_inches(height)}")
    weight = st.number_input("Weight (kg)", min_value=20, max_value=500, value=70)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"])
    country = st.selectbox("Country", ["United States", "India", "United Kingdom", "Canada", "Australia", "Other"])
    goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintenance", "Improve Stamina"])
    dietary_preference = st.selectbox("Dietary Preference", ["No Restrictions", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo"])
    allergies = st.text_input("Allergies (comma-separated):")
    workout_days = st.slider("Workout days per week", 1, 7, 4)
    workout_duration = st.slider("Workout duration (minutes)", 30, 120, 60)
    calculate_button = st.button("Generate Fitness Plan")

# Main content area
if calculate_button or st.session_state.fitness_plan_generated:
    if height > 0 and weight > 0:
        bmi = calculate_bmi(weight, height)
        category = categorize_bmi(bmi)
        weight_min, weight_max = ideal_weight_range(height)
        bmr = calculate_bmr(gender, weight, height, age)
        daily_calories = calculate_daily_calorie_needs(bmr, activity_level, goal)

        st.session_state.user_data.update({
            'Name': name,
            'Age': age,
            'Height': f"{height} cm ({cm_to_feet_inches(height)})",
            'Weight': f"{weight} kg",
            'Gender': gender,
            'BMI': f"{bmi:.2f}",
            'Category': category,
            'Daily Calorie Needs': f"{daily_calories} kcal"
        })

        if not st.session_state.fitness_plan_generated:
            # Generate meal plan and workout plan only if not already generated
            dietary_restrictions = f"{dietary_preference}. "
            dietary_restrictions += f"Allergies: {allergies}. " if allergies else ""
            with st.spinner("Generating meal plan..."):
                st.session_state.meal_plan = generate_meal_plan(daily_calories, dietary_restrictions)
            with st.spinner("Generating workout plan..."):
                st.session_state.workout_plan = generate_workout_plan(goal, workout_days, workout_duration)
            st.session_state.fitness_plan_generated = True

        # Section 1: Health Profile
        st.header("Your Health Profile")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<p class='big-font'>BMI: {bmi:.2f}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='big-font'>Category: {category}</p>", unsafe_allow_html=True)
        with col2:
            st.metric(label="Ideal Weight Range", value=f"{weight_min:.1f} - {weight_max:.1f} kg")
        with col3:
            st.metric(label="Daily Calorie Needs", value=f"{daily_calories} kcal")
        st.progress(min(1.0, max(0.0, (bmi - 15) / 25)))

        # Section 2: Meal Plan
        st.header("Your Personalized Meal Plan")
        with st.expander("View 7-Day Meal Plan", expanded=True):
            st.write(st.session_state.meal_plan)

        # Section 3: Workout Plan
        st.header("Your Personalized Workout Plan")
        with st.expander("View Weekly Workout Plan", expanded=True):
            st.write(st.session_state.workout_plan)

        # Section 4: Progress Tracking
        st.header("Track Your Progress")
        with st.expander("Set Goals and Track Progress", expanded=True):
            st.info("Setting realistic goals is crucial for your health and success. Gradual weight changes are generally safer and more sustainable. Always consult a healthcare professional before starting any new diet or exercise program.")

            goal_weight = st.number_input("Set your goal weight (kg)",
                                          min_value=0.0,
                                          value=float(weight),
                                          step=0.1)

            if goal_weight < weight_min:
                st.warning(f"Your goal weight of {goal_weight:.1f} kg is below the recommended minimum of {weight_min:.1f} kg for your height. Consider consulting a healthcare professional.")
            elif goal_weight > weight_max:
                st.warning(f"Your goal weight of {goal_weight:.1f} kg is above the recommended maximum of {weight_max:.1f} kg for your height. Consider consulting a healthcare professional.")
            else:
                st.success(f"Your goal weight of {goal_weight:.1f} kg is within the recommended range for your height.")

            weeks = st.slider("Timeframe (weeks)", 1, 52, 12)

            if st.button("Calculate Plan"):
                weight_diff = goal_weight - weight
                if weeks > 0:
                    weekly_change = weight_diff / weeks
                else:
                    st.error("Please select a timeframe greater than 0 weeks.")
                    st.stop()

                safe_loss_rate = 0.9  # kg per week
                safe_gain_rate = 0.5  # kg per week

                if abs(weekly_change) < 0.001:  # To handle floating point precision issues
                    st.success("Your current weight is already at your goal weight. Focus on maintaining your current weight and overall health.")
                elif weight_diff < 0:  # Weight loss
                    if abs(weekly_change) > safe_loss_rate:
                        st.warning(f"Your goal requires losing {abs(weekly_change):.2f} kg per week, which exceeds the recommended safe rate of {safe_loss_rate} kg per week for weight loss.")
                        adjusted_weeks = math.ceil(abs(weight_diff) / safe_loss_rate)
                        st.write(f"Consider extending your timeframe to {adjusted_weeks} weeks for a safer rate of weight loss.")
                    else:
                        st.success(f"Your goal of losing {abs(weekly_change):.2f} kg per week is within safe limits.")
                else:  # Weight gain
                    if weekly_change > safe_gain_rate:
                        st.warning(f"Your goal requires gaining {weekly_change:.2f} kg per week, which exceeds the recommended safe rate of {safe_gain_rate} kg per week for weight gain.")
                        adjusted_weeks = math.ceil(weight_diff / safe_gain_rate)
                        st.write(f"Consider extending your timeframe to {adjusted_weeks} weeks for a safer rate of weight gain.")
                    else:
                        st.success(f"Your goal of gaining {weekly_change:.2f} kg per week is within safe limits.")

                st.write(f"To reach your goal of {goal_weight:.1f} kg from your current weight of {weight:.1f} kg in {weeks} weeks:")
                st.write(f"Aim to {'lose' if weight_diff < 0 else 'gain'} about {abs(weekly_change):.2f} kg per week.")

                total_change = abs(weight_diff)
                st.write(f"Total {'weight loss' if weight_diff < 0 else 'weight gain'} goal: {total_change:.2f} kg")

        # Section 5: PDF Download
        st.header("Download Your Fitness Plan")
        if st.button("Generate PDF"):
            pdf = export_as_pdf(
                st.session_state.user_data,
                st.session_state.meal_plan,
                st.session_state.workout_plan
            )
            html = create_download_link(pdf, "FitTrack_Pro_Fitness_Plan.pdf")
            st.markdown(html, unsafe_allow_html=True)

    else:
        st.error("Please enter valid height and weight values.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>FitTrack Pro is designed for informational purposes only. Always consult with a healthcare professional before starting any new diet or exercise program.</p>", unsafe_allow_html=True)
