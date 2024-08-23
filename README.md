# FitTrack Pro 🏋️‍♂️ - Your Advanced Personal Fitness Companion

**FitTrack Pro** is an innovative and comprehensive fitness application designed to help you achieve your personal health and fitness goals. Whether you're aiming to lose weight, gain muscle, or maintain your current physique, FitTrack Pro offers personalized meal plans, workout routines, and progress tracking features tailored just for you.

## Overview

FitTrack Pro is built for anyone looking to take control of their fitness journey. From beginners to seasoned athletes, this application provides customized recommendations based on your unique body metrics and fitness goals. By integrating cutting-edge AI and machine learning, FitTrack Pro delivers accurate, actionable insights that can help you reach your desired outcomes faster and more efficiently.

## Features

- **Personalized Meal Plans**: Generate a 7-day meal plan based on your dietary preferences, calorie needs, and restrictions.
- **Custom Workout Plans**: Receive a detailed weekly workout schedule tailored to your fitness goals and availability.
- **BMI and BMR Calculations**: Instantly calculate your Body Mass Index (BMI) and Basal Metabolic Rate (BMR) to understand your body's needs.
- **Progress Tracking**: Set and track your fitness goals with easy-to-understand metrics and visualizations.
- **Light and Dark Modes**: Switch between light and dark themes to suit your environment and preferences.


## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Streamlit
- FPDF
- Google Generative AI (Gemini) API key

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/SauravSrivastav/FitTrack-Pro.git
    cd FitTrack-Pro
    ```

2. **Create and Activate a Virtual Environment:**

    - **For Windows:**

      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

    - **For macOS/Linux:**

      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the Google Generative AI API key:**

    Replace the placeholder API key in the code with your actual API key from Google Generative AI.

5. **Run the application locally:**

    ```bash
    streamlit run app.py
    ```

6. **Deactivate the Virtual Environment (When Done):**

    ```bash
    deactivate
    ```

### Usage

1. Fill in your personal details like name, age, height, weight, and fitness goals in the sidebar.
2. Generate your personalized meal and workout plans.
3. Download your plans as a PDF or track your progress directly within the app.

## Contributing

Contributions are welcome! If you'd like to improve FitTrack Pro, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
