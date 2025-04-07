import json
from datetime import datetime

def save_report(workout_type, reps, duration, mode="default", filename="reports.json"):
    calories_per_rep = {
        "pushups": 0.29,  # average kcal burned per pushup
        "squats": 0.32,
        "bicep_curls": 0.28
    }
    calories = round(calories_per_rep.get(workout_type, 0.3) * reps, 2)

    report = {
        "workout": workout_type,
        "timestamp": datetime.utcnow().isoformat(),
        "reps": reps,
        "duration_sec": duration,
        "mode": mode,
        "calories": calories
    }

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(report)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    return report