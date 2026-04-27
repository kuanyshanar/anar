import json
import os


BASE_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")


DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}



def load_json(path, default_data):
    
    if not os.path.exists(path):
        save_json(path, default_data)
        return default_data.copy()

    
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    
    except Exception:
        save_json(path, default_data)
        return default_data.copy()



def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)



def load_settings():
    settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)


    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value

    return settings



def save_settings(settings):
    save_json(SETTINGS_FILE, settings)



def load_leaderboard():
    return load_json(LEADERBOARD_FILE, [])



def save_score(username, score, distance, coins):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "name": username,
        "score": int(score),
        "distance": int(distance),
        "coins": int(coins)
    })


    leaderboard.sort(key=lambda item: item["score"], reverse=True)
  
    leaderboard = leaderboard[:10]

    save_json(LEADERBOARD_FILE, leaderboard)