import json
import os
from util import Dialog

DB_FILE = "leaderboard.json"

def save_score(user_id, user_name, topic, total_correct):
    data = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    user_id = str(user_id)

    # Перевіряємо наявність користувача та всіх необхідних ключів
    if user_id not in data:
        data[user_id] = {'name': user_name, 'scores': {}, 'total': 0, 'level': 1, 'achievements': []}

    # Перевірка наявності ключа досягнень для старих записів
    if 'achievements' not in data[user_id]:
        data[user_id]['achievements'] = []

    if 'scores' not in data[user_id]:
        data[user_id]['scores'] = {}

    # Оновлюємо бали по конкретній темі
    current_topic_score = data[user_id]['scores'].get(topic, 0)
    if total_correct > current_topic_score:
        data[user_id]['scores'][topic] = total_correct

    # Перерахунок загальної кількості балів
    all_scores = data[user_id]['scores'].values()
    data[user_id]['total'] = sum(all_scores)

    # Перерахунок рівня (наприклад, кожні 5 балів — новий рівень)
    total = data[user_id]['total']
    data[user_id]['level'] = (total // 5) + 1

    # АВТОМАТИЧНА ПЕРЕВІРКА ДОСЯГНЕНЬ
    new_achievement = None
    for count, name in Dialog.QUIZ_ACHIEVEMENTS.items():
        if total >= count and name not in data[user_id]['achievements']:
            data[user_id]['achievements'].append(name)
            new_achievement = name  # Повернемо останнє отримане для вітання

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return new_achievement  # Функція повертає назву нового досягнення, якщо воно є

def get_user_data(user_id):
    """Повертає дані конкретного користувача або None"""
    if not os.path.exists(DB_FILE):
        return None
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(str(user_id))

def get_leaderboard():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return []

    return sorted(data.values(), key=lambda x: x['total'], reverse=True)[:10]