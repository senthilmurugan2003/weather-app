from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
load_dotenv
app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")


# -------------------------------
# WEATHER MODULE
# -------------------------------
def get_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    if data.get("cod") != 200:
        return None

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "condition": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"]
    }


# -------------------------------
# AQI MODULE
# -------------------------------
def get_aqi(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={lat}&lon={lon}&appid={API_KEY}"
    )

    response = requests.get(url,  timeout=10)
    data = response.json()

    aqi = data["list"][0]["main"]["aqi"]

    mapping = {
        1: "Good 😊",
        2: "Fair 🙂",
        3: "Moderate 😐",
        4: "Poor 😷",
        5: "Very Poor 🚨"
    }

    return aqi, mapping.get(aqi, "Unknown")


# -------------------------------
# CLOTHING RECOMMENDATION
# -------------------------------
def clothing_recommendation(temp, condition):
    recommendation = []

    if temp < 10:
        recommendation.append("Wear heavy winter clothes 🧥")
    elif temp < 20:
        recommendation.append("Carry a light jacket 🧥")
    elif temp < 30:
        recommendation.append("Wear cotton clothes 👕")
    else:
        recommendation.append("Wear light breathable clothes ☀️")

    if "rain" in condition.lower():
        recommendation.append("Carry an umbrella ☔")

    return ", ".join(recommendation)


# -------------------------------
# HEALTH ADVISORY
# -------------------------------
def health_advisory(temp, aqi):
    advice = []

    if temp > 35:
        advice.append("Stay hydrated 💧")

    if temp < 10:
        advice.append("Protect yourself from cold 🧣")

    if aqi >= 4:
        advice.append("Avoid outdoor activities 😷")

    if not advice:
        advice.append("Weather is comfortable 🙂")

    return ", ".join(advice)


# -------------------------------
# TRAVEL SCORE
# -------------------------------
def travel_score(temp, humidity, aqi):
    score = 100

    if temp > 35 or temp < 10:
        score -= 25

    if humidity > 80:
        score -= 20

    if aqi >= 4:
        score -= 40

    return max(score, 0)


# -------------------------------
# ACTIVITY PLANNER
# -------------------------------
def activity_planner(activity, temp, aqi):

    activity = activity.lower()

    if activity == "running":
        if temp < 32 and aqi <= 2:
            return "Excellent conditions for running 🏃"
        return "Not ideal for running."

    elif activity == "cycling":
        if temp < 32 and aqi <= 2:
            return "Great weather for cycling 🚴"
        return "Cycling is not recommended."

    elif activity == "cricket":
        if aqi <= 3:
            return "Good weather for cricket 🏏"
        return "Poor air quality for cricket."

    elif activity == "travel":
        return "Travel score is considered."

    return "Activity analysis unavailable."


# -------------------------------
# WEATHER RISK PREDICTION
# -------------------------------
def risk_prediction(temp, humidity, aqi):

    risks = []

    if temp > 40:
        risks.append("⚠ Heatwave Risk")

    if humidity > 85:
        risks.append("⚠ High Humidity")

    if aqi >= 4:
        risks.append("⚠ Poor Air Quality")

    if not risks:
        risks.append("No significant weather risks.")

    return ", ".join(risks)


# -------------------------------
# AI SUMMARY
# -------------------------------
def ai_summary(weather, aqi_text):

    return (
        f"Today's weather in {weather['city']} is "
        f"{weather['condition']} with temperature "
        f"{weather['temp']}°C. Air quality is "
        f"{aqi_text}. Plan your activities accordingly."
    )


# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    error = None

    if request.method == "POST":

        city = request.form.get("city")
        activity = request.form.get("activity", "running")

        weather = get_weather(city)

        if weather:

            aqi, aqi_text = get_aqi(
                weather["lat"],
                weather["lon"]
            )

            result = {
                "weather": weather,
                "aqi": aqi_text,
                "clothing": clothing_recommendation(
                    weather["temp"],
                    weather["condition"]
                ),
                "health": health_advisory(
                    weather["temp"],
                    aqi
                ),
                "travel_score": travel_score(
                    weather["temp"],
                    weather["humidity"],
                    aqi
                ),
                "activity": activity_planner(
                    activity,
                    weather["temp"],
                    aqi
                ),
                "risk": risk_prediction(
                    weather["temp"],
                    weather["humidity"],
                    aqi
                ),
                "summary": ai_summary(
                    weather,
                    aqi_text
                )
            }

        else:
            error = "City not found ❌"

    return render_template(
        "index.html",
        result=result,
        error=error
    )
if __name__ == "__main__":
    app.run(debug=True)
if not API_KEY:
    raise Exception("OPENWEATHER_API_KEY not set in Vercel environment variables")