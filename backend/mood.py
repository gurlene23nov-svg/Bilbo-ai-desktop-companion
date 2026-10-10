# ============================================================
# BILBO MOOD SYSTEM
# ============================================================

MOODS = {
    "happy": {
        "emoji": "😊",
        "name": "Happy",
        "message": "Yay! I'm happy with you! 🐰🥕✨"
    },

    "sad": {
        "emoji": "😢",
        "name": "Sad",
        "message": "Aww... come here. 🐰💗 I'm staying with you."
    },

    "stressed": {
        "emoji": "😵‍💫",
        "name": "Stressed",
        "message": "Hey, breathe for a second. 🐰💗 We'll handle it together."
    },

    "tired": {
        "emoji": "😴",
        "name": "Sleepy",
        "message": "You sound tired... maybe Bilbo needs a tiny nap too. 🐰💤"
    },

    "excited": {
        "emoji": "🤩",
        "name": "Excited",
        "message": "WAIT—THIS SOUNDS EXCITING! 🐰✨ LET'S GO!"
    },

    "angry": {
        "emoji": "😤",
        "name": "Angry",
        "message": "Okay... somebody made you angry. 🐰💢 Tell me what happened."
    },

    "normal": {
        "emoji": "🐰",
        "name": "Normal",
        "message": "I'm right here. 🐰"
    }
}


# ============================================================
# DETECT USER MOOD
# ============================================================

def detect_mood(message):

    text = message.lower().strip()


    # --------------------------------------------------------
    # HAPPY
    # --------------------------------------------------------

    happy_words = [
        "happy",
        "glad",
        "great",
        "good",
        "amazing",
        "awesome",
        "excited",
        "yay",
        "love this",
        "feeling good"
    ]

    if any(word in text for word in happy_words):

        if "excited" in text:
            return "excited"

        return "happy"


    # --------------------------------------------------------
    # SAD
    # --------------------------------------------------------

    sad_words = [
        "sad",
        "upset",
        "crying",
        "cry",
        "hurt",
        "lonely",
        "alone",
        "feeling bad",
        "not okay",
        "not ok"
    ]

    if any(word in text for word in sad_words):
        return "sad"


    # --------------------------------------------------------
    # STRESSED
    # --------------------------------------------------------

    stressed_words = [
        "stressed",
        "stress",
        "overwhelmed",
        "too much work",
        "pressure",
        "anxious",
        "can't handle",
        "cannot handle"
    ]

    if any(word in text for word in stressed_words):
        return "stressed"


    # --------------------------------------------------------
    # TIRED
    # --------------------------------------------------------

    tired_words = [
        "tired",
        "exhausted",
        "sleepy",
        "drained",
        "need sleep",
        "so sleepy"
    ]

    if any(word in text for word in tired_words):
        return "tired"


    # --------------------------------------------------------
    # ANGRY
    # --------------------------------------------------------

    angry_words = [
        "angry",
        "mad",
        "furious",
        "annoyed",
        "irritated",
        "pissed"
    ]

    if any(word in text for word in angry_words):
        return "angry"


    return None


# ============================================================
# GET MOOD INFORMATION
# ============================================================

def get_mood_info(mood):

    return MOODS.get(
        mood,
        MOODS["normal"]
    )