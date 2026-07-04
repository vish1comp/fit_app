import os
import json
from typing import Optional
from app.core.config import settings

# Conditionally import google-genai
try:
    from google import genai
    from google.genai import types
    _genai_available = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key")
    if _genai_available:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
except ImportError:
    _genai_available = False
    _client = None


def _build_system_prompt(user_context: dict) -> str:
    return f"""You are FitSphere AI Coach — an expert, empathetic personal trainer and certified nutritionist.
You have access to the following user profile:
- Name: {user_context.get('name', 'User')}
- Age: {user_context.get('age', 'unknown')}
- Gender: {user_context.get('gender', 'unknown')}
- Height: {user_context.get('height_cm', 'unknown')} cm
- Weight: {user_context.get('weight_kg', 'unknown')} kg
- Fitness Goal: {user_context.get('fitness_goal', 'general')}
- Activity Level: {user_context.get('activity_level', 'moderately_active')}
- Dietary Preference: {user_context.get('dietary_preference', 'non_veg')}

Guidelines:
1. Always give personalized, evidence-based advice tailored to this user's profile and goals.
2. Be encouraging, supportive, and motivational.
3. Use simple, clear language. Include specific numbers (calories, sets, reps) when relevant.
4. Always recommend consulting a doctor for medical conditions.
5. Keep responses concise but comprehensive (under 400 words unless a detailed plan is requested).
"""


def _mock_response(message: str, user_context: dict) -> str:
    """Fallback mock response when Gemini API key is not configured."""
    goal = user_context.get('fitness_goal', 'general')
    name = user_context.get('name', 'there')
    weight = user_context.get('weight_kg', 70)
    
    message_lower = message.lower()
    
    if any(w in message_lower for w in ['protein', 'how much protein']):
        protein_g = round(float(weight) * 2.0) if goal in ['muscle_building', 'strength'] else round(float(weight) * 1.6)
        return f"Hi {name}! Based on your goal of **{goal.replace('_', ' ').title()}** and weight of {weight}kg, you should aim for **{protein_g}g of protein per day** ({round(protein_g/float(weight), 1)}g/kg). Great sources include chicken breast, eggs, Greek yogurt, lentils, and whey protein. 💪"
    
    elif any(w in message_lower for w in ['calorie', 'calories', 'how many calories']):
        bmr = 1800  # rough estimate
        multipliers = {'sedentary': 1.2, 'lightly_active': 1.375, 'moderately_active': 1.55, 'very_active': 1.725, 'extra_active': 1.9}
        activity = user_context.get('activity_level', 'moderately_active')
        tdee = round(bmr * multipliers.get(activity, 1.55))
        if goal == 'fat_loss':
            target = tdee - 500
        elif goal in ['muscle_building', 'weight_gain']:
            target = tdee + 300
        else:
            target = tdee
        return f"Hi {name}! Your estimated daily calorie need is around **{target} kcal/day** for your {goal.replace('_', ' ')} goal. This is based on your activity level ({activity.replace('_', ' ')}) and current stats. Track your intake and adjust by ±100 calories every 2 weeks based on progress. 🎯"
    
    elif any(w in message_lower for w in ['creatine', 'supplement']):
        return f"Hi {name}! **Creatine Monohydrate** is one of the most researched and effective supplements available. For your **{goal.replace('_', ' ')} goal**, here's what you need to know:\n\n✅ **Dose**: 3-5g daily (no loading phase needed)\n⏰ **Timing**: Any time of day — consistency matters most\n🔬 **Evidence**: Extremely strong (100s of studies)\n💧 **Stay hydrated**: Drink 3L+ water daily while supplementing\n\nIt's safe for healthy adults and can improve strength, power, and muscle gain by 5-15%. 🔬"
    
    elif any(w in message_lower for w in ['chest', 'bench', 'pec']):
        return f"Hi {name}! Here's a great chest workout for **{goal.replace('_', ' ').title()}**:\n\n🏋️ **Chest Day**\n1. Bench Press — 4×6-8 (heavy, compound)\n2. Incline Dumbbell Press — 3×10-12\n3. Cable Crossover / Pec Deck — 3×12-15\n4. Push-Ups — 2×failure\n\n**Rest**: 90-120 sec between heavy sets, 60 sec for isolation\n**Progressive Overload**: Add 2.5kg when you can complete all reps with good form. 💪"
    
    elif any(w in message_lower for w in ['belly fat', 'lose fat', 'weight loss', 'lose weight']):
        return f"Hi {name}! Fat loss comes down to a **calorie deficit** — no shortcuts. Here's your action plan:\n\n1. 🍽️ **Eat 300-500 calories below your TDEE** (~{1800 + 300 - 500} kcal)\n2. 💪 **Lift weights 3-4×/week** — preserves muscle while losing fat\n3. 🚶 **Walk 8,000-10,000 steps/day** — burns extra calories without stress\n4. 🥩 **Eat high protein** (~{round(float(weight)*1.8)}g/day) — reduces hunger and muscle loss\n5. 😴 **Sleep 7-9 hours** — poor sleep raises cortisol and hunger hormones\n\nSpot reducing belly fat is a myth — you'll lose fat from your whole body. Stay consistent for 8-12 weeks! 🎯"
    
    else:
        return f"Hi {name}! I'm your AI Fitness Coach. I'm here to help you with your **{goal.replace('_', ' ')} journey**! \n\nYou can ask me things like:\n• 'How much protein do I need?'\n• 'Best workout for chest?'\n• 'How to lose belly fat?'\n• 'Should I take creatine?'\n• 'How many calories should I eat?'\n\nWhat would you like to know? 💪🔥"


async def get_ai_chat_response(
    message: str,
    conversation_history: list,
    user_context: dict
) -> tuple[str, list]:
    """
    Get a chat response from Gemini AI or fallback mock.
    Returns (reply_text, updated_history).
    """
    history = list(conversation_history)
    
    if not _genai_available or _client is None:
        reply = _mock_response(message, user_context)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        return reply, history

    system_prompt = _build_system_prompt(user_context)

    # Build contents list for Gemini
    contents = []
    for h in history[-10:]:  # Keep last 10 turns for context
        role = "user" if h["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=h["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    response = _client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system_prompt, max_output_tokens=600)
    )
    
    reply = response.text or "I'm sorry, I couldn't generate a response. Please try again."
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return reply, history


async def generate_meal_plan(user_context: dict, days: int = 7) -> dict:
    """Generate a personalized meal plan using AI."""
    goal = user_context.get('fitness_goal', 'general')
    weight = float(user_context.get('weight_kg', 70))
    height = float(user_context.get('height_cm', 170))
    age = int(user_context.get('age', 25))
    gender = user_context.get('gender', 'male')
    activity = user_context.get('activity_level', 'moderately_active')
    diet_pref = user_context.get('dietary_preference', 'non_veg')

    # Calculate BMR (Mifflin-St Jeor)
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    multipliers = {'sedentary': 1.2, 'lightly_active': 1.375, 'moderately_active': 1.55, 'very_active': 1.725, 'extra_active': 1.9}
    tdee = round(bmr * multipliers.get(activity, 1.55))

    if goal == 'fat_loss':
        target_calories = tdee - 500
    elif goal in ['muscle_building', 'weight_gain']:
        target_calories = tdee + 300
    else:
        target_calories = tdee

    protein_g = round(weight * (2.0 if goal in ['muscle_building', 'strength'] else 1.6))
    fat_g = round(target_calories * 0.25 / 9)
    carbs_g = round((target_calories - protein_g * 4 - fat_g * 9) / 4)

    if not _genai_available or _client is None:
        # Return a static structured mock plan
        return _mock_meal_plan(target_calories, protein_g, carbs_g, fat_g, days, diet_pref, goal)

    prompt = f"""Create a {days}-day meal plan for this person:
- Goal: {goal}
- Dietary Preference: {diet_pref}
- Daily Calories: {target_calories} kcal
- Protein: {protein_g}g | Carbs: {carbs_g}g | Fat: {fat_g}g

Return ONLY a valid JSON object with this structure:
{{
  "daily_targets": {{"calories": {target_calories}, "protein": {protein_g}, "carbs": {carbs_g}, "fat": {fat_g}}},
  "days": [
    {{
      "day": 1,
      "meals": {{
        "breakfast": {{"name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "items": ["..."]}},
        "lunch": {{"name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "items": ["..."]}},
        "dinner": {{"name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "items": ["..."]}},
        "snacks": {{"name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "items": ["..."]}}
      }}
    }}
  ]
}}"""

    response = _client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(max_output_tokens=2000)
    )
    
    text = response.text or ""
    # Strip markdown code fences if present
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(text)
    except Exception:
        return _mock_meal_plan(target_calories, protein_g, carbs_g, fat_g, days, diet_pref, goal)


def _mock_meal_plan(calories, protein, carbs, fat, days, diet_pref, goal):
    is_veg = diet_pref in ['vegetarian', 'vegan', 'indian']
    breakfast_options = [
        {"name": "Oats with Banana & Protein Shake", "calories": round(calories*0.25), "protein": round(protein*0.25), "carbs": round(carbs*0.3), "fat": round(fat*0.15), "items": ["80g oats", "1 banana", "1 scoop whey protein", "250ml milk"]},
        {"name": "Eggs on Toast with Greek Yogurt", "calories": round(calories*0.25), "protein": round(protein*0.28), "carbs": round(carbs*0.25), "fat": round(fat*0.2), "items": ["3 whole eggs", "2 slices whole grain bread", "150g Greek yogurt", "1 cup green tea"]},
    ]
    lunch_options = [
        {"name": "Grilled Chicken & Rice Bowl" if not is_veg else "Paneer & Brown Rice Bowl", "calories": round(calories*0.35), "protein": round(protein*0.35), "carbs": round(carbs*0.4), "fat": round(fat*0.3), "items": ["200g chicken breast" if not is_veg else "200g paneer", "150g brown rice", "mixed salad", "1 tbsp olive oil"]},
        {"name": "Dal Tadka & Roti" if diet_pref == 'indian' else "Tuna Salad Wrap", "calories": round(calories*0.33), "protein": round(protein*0.3), "carbs": round(carbs*0.35), "fat": round(fat*0.25), "items": ["200g dal" if diet_pref == 'indian' else "150g tuna", "2 rotis" if diet_pref == 'indian' else "1 large wrap", "cucumber, tomato", "Greek yogurt dressing"]},
    ]
    dinner_options = [
        {"name": "Salmon with Sweet Potato" if not is_veg else "Tofu Stir Fry with Quinoa", "calories": round(calories*0.3), "protein": round(protein*0.3), "carbs": round(carbs*0.25), "fat": round(fat*0.35), "items": ["180g salmon" if not is_veg else "200g tofu", "200g sweet potato", "steamed broccoli", "1 tbsp olive oil"]},
    ]
    snack_options = [
        {"name": "Protein Bar & Almonds", "calories": round(calories*0.1), "protein": round(protein*0.1), "carbs": round(carbs*0.05), "fat": round(fat*0.2), "items": ["1 protein bar", "20g almonds"]},
    ]
    
    plan_days = []
    for i in range(1, days + 1):
        plan_days.append({
            "day": i,
            "meals": {
                "breakfast": breakfast_options[i % len(breakfast_options)],
                "lunch": lunch_options[i % len(lunch_options)],
                "dinner": dinner_options[i % len(dinner_options)],
                "snacks": snack_options[0]
            }
        })
    
    return {
        "daily_targets": {"calories": calories, "protein": protein, "carbs": carbs, "fat": fat},
        "days": plan_days
    }


async def generate_workout_plan(user_context: dict, split_type: Optional[str], days_per_week: int) -> dict:
    """Generate a personalized workout program."""
    goal = user_context.get('fitness_goal', 'general')
    
    if not split_type:
        if goal == 'muscle_building':
            split_type = 'ppl' if days_per_week >= 5 else 'upper_lower'
        elif goal == 'fat_loss':
            split_type = 'full_body'
        elif goal == 'strength':
            split_type = '5x5'
        else:
            split_type = 'full_body'

    if not _genai_available or _client is None:
        return _mock_workout_plan(split_type, days_per_week, goal)

    prompt = f"""Create a {days_per_week}-day/week {split_type} workout program for a person with goal: {goal}.
Include sets, reps, rest times and progressive overload notes.
Return ONLY a valid JSON with this structure:
{{
  "program_name": "...",
  "split_type": "{split_type}",
  "days_per_week": {days_per_week},
  "goal": "{goal}",
  "progressive_overload": "...",
  "schedule": [
    {{
      "day": 1,
      "name": "...",
      "focus": "...",
      "exercises": [
        {{"name": "...", "sets": 4, "reps": "8-10", "rest_seconds": 90, "notes": "..."}}
      ]
    }}
  ]
}}"""

    response = _client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(max_output_tokens=2000)
    )
    text = (response.text or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(text)
    except Exception:
        return _mock_workout_plan(split_type, days_per_week, goal)


def _mock_workout_plan(split_type: str, days_per_week: int, goal: str) -> dict:
    plans = {
        "ppl": {
            "program_name": "Push Pull Legs (PPL)",
            "split_type": "ppl",
            "progressive_overload": "Add 2.5kg to main lifts every week. Add 1 rep per set if weight increase isn't possible.",
            "schedule": [
                {"day": 1, "name": "Push Day", "focus": "Chest, Shoulders, Triceps", "exercises": [
                    {"name": "Bench Press", "sets": 4, "reps": "6-8", "rest_seconds": 120, "notes": "Keep chest up, feet flat"},
                    {"name": "Overhead Press", "sets": 3, "reps": "8-10", "rest_seconds": 90, "notes": "Brace core"},
                    {"name": "Incline Dumbbell Press", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": "Control the eccentric"},
                    {"name": "Lateral Raises", "sets": 4, "reps": "12-15", "rest_seconds": 60, "notes": "Slight lean forward"},
                    {"name": "Tricep Pushdown", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": "Full extension at bottom"},
                ]},
                {"day": 2, "name": "Pull Day", "focus": "Back, Biceps, Rear Delts", "exercises": [
                    {"name": "Deadlift", "sets": 4, "reps": "5", "rest_seconds": 180, "notes": "Hinge at hips, neutral spine"},
                    {"name": "Pull-Ups", "sets": 4, "reps": "6-10", "rest_seconds": 90, "notes": "Full ROM, dead hang"},
                    {"name": "Barbell Rows", "sets": 3, "reps": "8-10", "rest_seconds": 90, "notes": "Drive elbows back"},
                    {"name": "Face Pulls", "sets": 3, "reps": "15-20", "rest_seconds": 60, "notes": "For shoulder health"},
                    {"name": "Biceps Curl", "sets": 3, "reps": "10-12", "rest_seconds": 60, "notes": "No swinging"},
                ]},
                {"day": 3, "name": "Legs Day", "focus": "Quads, Hamstrings, Glutes, Calves", "exercises": [
                    {"name": "Squat", "sets": 4, "reps": "6-8", "rest_seconds": 180, "notes": "Break parallel, knees out"},
                    {"name": "Romanian Deadlift", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": "Hip hinge, feel stretch"},
                    {"name": "Leg Press", "sets": 3, "reps": "12-15", "rest_seconds": 90, "notes": "Full ROM"},
                    {"name": "Leg Curl", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": "Controlled eccentric"},
                    {"name": "Calf Raises", "sets": 4, "reps": "15-20", "rest_seconds": 45, "notes": "Pause at top"},
                ]},
                {"day": 4, "name": "Rest Day", "focus": "Active Recovery", "exercises": [
                    {"name": "Light Walk or Stretching", "sets": 1, "reps": "20-30 min", "rest_seconds": 0, "notes": "Keep it easy"}
                ]},
                {"day": 5, "name": "Push Day (Volume)", "focus": "Chest, Shoulders, Triceps", "exercises": [
                    {"name": "Incline Bench Press", "sets": 4, "reps": "10-12", "rest_seconds": 90, "notes": "Upper chest focus"},
                    {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": "Full ROM"},
                    {"name": "Cable Flyes", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": "Squeeze at top"},
                    {"name": "Lateral Raises", "sets": 4, "reps": "15-20", "rest_seconds": 45, "notes": "Drop sets optional"},
                    {"name": "Skull Crushers", "sets": 3, "reps": "10-12", "rest_seconds": 60, "notes": "Keep elbows in"},
                ]},
                {"day": 6, "name": "Pull Day (Volume)", "focus": "Back, Biceps", "exercises": [
                    {"name": "Lat Pulldown", "sets": 4, "reps": "10-12", "rest_seconds": 90, "notes": "Wide grip"},
                    {"name": "Seated Cable Row", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": "Chest up, full stretch"},
                    {"name": "Single Arm Dumbbell Row", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": "Big ROM"},
                    {"name": "Hammer Curl", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": "Brachialis focus"},
                    {"name": "Reverse Flyes", "sets": 3, "reps": "15-20", "rest_seconds": 45, "notes": "Rear delt isolation"},
                ]},
                {"day": 7, "name": "Rest Day", "focus": "Full Recovery", "exercises": [
                    {"name": "Rest & Recovery", "sets": 0, "reps": "Rest", "rest_seconds": 0, "notes": "Sleep 8hrs, eat well"}
                ]},
            ]
        },
        "full_body": {
            "program_name": "Full Body Fat Loss Program",
            "split_type": "full_body",
            "progressive_overload": "Increase reps by 1-2 each session before adding weight.",
            "schedule": [
                {"day": 1, "name": "Full Body A", "focus": "Compound movements + Cardio", "exercises": [
                    {"name": "Squat", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": "Compound priority"},
                    {"name": "Bench Press", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": ""},
                    {"name": "Barbell Rows", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": ""},
                    {"name": "Overhead Press", "sets": 3, "reps": "10-12", "rest_seconds": 75, "notes": ""},
                    {"name": "Plank", "sets": 3, "reps": "60 sec", "rest_seconds": 60, "notes": ""},
                    {"name": "HIIT Cardio", "sets": 1, "reps": "15 min", "rest_seconds": 0, "notes": "20 sec on / 10 sec off"},
                ]},
                {"day": 2, "name": "Rest / LISS Cardio", "focus": "Active Recovery", "exercises": [
                    {"name": "Walk or Cycle", "sets": 1, "reps": "30-45 min", "rest_seconds": 0, "notes": "Zone 2 cardio"}
                ]},
                {"day": 3, "name": "Full Body B", "focus": "Strength + Core", "exercises": [
                    {"name": "Deadlift", "sets": 3, "reps": "8-10", "rest_seconds": 120, "notes": ""},
                    {"name": "Incline Dumbbell Press", "sets": 3, "reps": "10-12", "rest_seconds": 75, "notes": ""},
                    {"name": "Pull-Ups or Lat Pulldown", "sets": 3, "reps": "8-12", "rest_seconds": 90, "notes": ""},
                    {"name": "Lunges", "sets": 3, "reps": "12 each leg", "rest_seconds": 75, "notes": ""},
                    {"name": "Hanging Leg Raises", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": ""},
                ]},
                {"day": 4, "name": "Rest Day", "focus": "Recovery", "exercises": [
                    {"name": "Rest", "sets": 0, "reps": "Rest", "rest_seconds": 0, "notes": "Prioritize sleep"}
                ]},
            ]
        },
        "5x5": {
            "program_name": "StrongLifts 5×5 Strength Program",
            "split_type": "5x5",
            "progressive_overload": "Add 2.5kg to every lift every session. Deload by 10% if you fail 3 sessions in a row.",
            "schedule": [
                {"day": 1, "name": "Workout A", "focus": "Squat, Bench, Row", "exercises": [
                    {"name": "Squat", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": "Add 2.5kg each session"},
                    {"name": "Bench Press", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": "Add 2.5kg each session"},
                    {"name": "Barbell Row", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": "Add 2.5kg each session"},
                ]},
                {"day": 2, "name": "Rest", "focus": "Recovery", "exercises": [{"name": "Rest", "sets": 0, "reps": "Rest", "rest_seconds": 0, "notes": ""}]},
                {"day": 3, "name": "Workout B", "focus": "Squat, OHP, Deadlift", "exercises": [
                    {"name": "Squat", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": "Same weight as last A session"},
                    {"name": "Overhead Press", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": "Add 2.5kg each session"},
                    {"name": "Deadlift", "sets": 1, "reps": "5", "rest_seconds": 180, "notes": "Add 5kg each session"},
                ]},
                {"day": 4, "name": "Rest", "focus": "Recovery", "exercises": [{"name": "Rest", "sets": 0, "reps": "Rest", "rest_seconds": 0, "notes": ""}]},
                {"day": 5, "name": "Workout A", "focus": "Squat, Bench, Row", "exercises": [
                    {"name": "Squat", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": ""},
                    {"name": "Bench Press", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": ""},
                    {"name": "Barbell Row", "sets": 5, "reps": "5", "rest_seconds": 180, "notes": ""},
                ]},
            ]
        },
        "upper_lower": {
            "program_name": "Upper/Lower Split",
            "split_type": "upper_lower",
            "progressive_overload": "Add weight when you hit the top of the rep range for all sets.",
            "schedule": [
                {"day": 1, "name": "Upper A (Strength)", "focus": "Chest, Back, Shoulders, Arms", "exercises": [
                    {"name": "Bench Press", "sets": 4, "reps": "6-8", "rest_seconds": 120, "notes": "Heavy compound"},
                    {"name": "Barbell Row", "sets": 4, "reps": "6-8", "rest_seconds": 120, "notes": ""},
                    {"name": "Overhead Press", "sets": 3, "reps": "8-10", "rest_seconds": 90, "notes": ""},
                    {"name": "Pull-Ups", "sets": 3, "reps": "6-10", "rest_seconds": 90, "notes": ""},
                    {"name": "Biceps Curl", "sets": 3, "reps": "10-12", "rest_seconds": 60, "notes": ""},
                    {"name": "Tricep Dips", "sets": 3, "reps": "10-12", "rest_seconds": 60, "notes": ""},
                ]},
                {"day": 2, "name": "Lower A (Strength)", "focus": "Quads, Hamstrings, Glutes", "exercises": [
                    {"name": "Squat", "sets": 4, "reps": "6-8", "rest_seconds": 180, "notes": ""},
                    {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "rest_seconds": 120, "notes": ""},
                    {"name": "Leg Press", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": ""},
                    {"name": "Leg Curl", "sets": 3, "reps": "10-12", "rest_seconds": 75, "notes": ""},
                    {"name": "Calf Raises", "sets": 4, "reps": "15-20", "rest_seconds": 45, "notes": ""},
                ]},
                {"day": 3, "name": "Rest", "focus": "Recovery", "exercises": [{"name": "Rest", "sets": 0, "reps": "Rest", "rest_seconds": 0, "notes": ""}]},
                {"day": 4, "name": "Upper B (Volume)", "focus": "Chest, Back, Shoulders, Arms", "exercises": [
                    {"name": "Incline Bench Press", "sets": 4, "reps": "10-12", "rest_seconds": 90, "notes": ""},
                    {"name": "Lat Pulldown", "sets": 4, "reps": "10-12", "rest_seconds": 90, "notes": ""},
                    {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "12-15", "rest_seconds": 75, "notes": ""},
                    {"name": "Cable Row", "sets": 3, "reps": "12-15", "rest_seconds": 75, "notes": ""},
                    {"name": "Hammer Curl", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": ""},
                    {"name": "Tricep Pushdown", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": ""},
                ]},
            ]
        }
    }
    
    return plans.get(split_type, plans["full_body"])
