from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import random
import json
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- GEMINI AI CONFIGURATION ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- DATABASE ---
users = {
    "player1": {
        "coins": 200, 
        "tickets": 0,
        "lifelines": {"5050": 1, "audience": 1, "phone": 1, "expert": 1}
    } 
}

active_game_answers = {}

# --- 100+ REAL MIX QUESTIONS ---
REAL_QUESTIONS = [
    # GK & India
    {"q": "Bharat ki rajdhani kya hai?", "correct": "New Delhi", "wrong": ["Mumbai", "Kolkata", "Chennai"]},
    {"q": "Sabse bada mahasagar kaunsa hai?", "correct": "Pacific Ocean", "wrong": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]},
    {"q": "Bharat ka rashtriya pakshi kaunsa hai?", "correct": "Mor", "wrong": ["Kauwa", "Tota", "Kabootar"]},
    {"q": "Duniya ka sabse uncha parvat kaunsa hai?", "correct": "Mount Everest", "wrong": ["K2", "Kanchenjunga", "Makalu"]},
    {"q": "Bharat mein kitne rajya hain?", "correct": "28", "wrong": ["27", "29", "30"]},
    {"q": "Japan ki currency kya hai?", "correct": "Yen", "wrong": ["Yuan", "Won", "Dollar"]},
    {"q": "Duniya ka sabse bada desert kaunsa hai?", "correct": "Sahara", "wrong": ["Thar", "Gobi", "Antarctic"]},
    {"q": "Bharat ka rashtriya pashu kaunsa hai?", "correct": "Bagh", "wrong": ["Sher", "Hathi", "Gaay"]},
    {"q": "Sabse lambi nadi kaunsi hai?", "correct": "Nile", "wrong": ["Ganga", "Amazon", "Yamuna"]},
    {"q": "Australia ki rajdhani kya hai?", "correct": "Canberra", "wrong": ["Sydney", "Melbourne", "Perth"]},
    {"q": "Bharat ka rashtriya phool kaunsa hai?", "correct": "Kamal", "wrong": ["Gulab", "Surajmukhi", "Champa"]},
    {"q": "Duniya ka sabse bada desh kaunsa hai (Area)?", "correct": "Russia", "wrong": ["Canada", "China", "USA"]},
    {"q": "Bharat ki sabse lambi nadi kaunsi hai?", "correct": "Ganga", "wrong": ["Yamuna", "Godavari", "Narmada"]},
    {"q": "Taj Mahal kis sheher mein hai?", "correct": "Agra", "wrong": ["Delhi", "Jaipur", "Lucknow"]},
    {"q": "United Nations ka headquarter kahan hai?", "correct": "New York", "wrong": ["Geneva", "Paris", "London"]},
    {"q": "Bharat ka sabse chhota rajya kaunsa hai?", "correct": "Goa", "wrong": ["Sikkim", "Tripura", "Manipur"]},
    {"q": "Duniya ka sabse bada island kaunsa hai?", "correct": "Greenland", "wrong": ["Australia", "Madagascar", "Borneo"]},
    {"q": "Kaunsa grah 'Red Planet' kahlata hai?", "correct": "Mars", "wrong": ["Venus", "Jupiter", "Saturn"]},
    {"q": "Chand par pehla kadam kisne rakha?", "correct": "Neil Armstrong", "wrong": ["Yuri Gagarin", "Buzz Aldrin", "Rakesh Sharma"]},
    {"q": "Sri Lanka ki rajdhani kya hai?", "correct": "Sri Jayawardenepura", "wrong": ["Colombo", "Kandy", "Galle"]},
    
    # Science
    {"q": "Pani ka rasayanik sutra kya hai?", "correct": "H2O", "wrong": ["CO2", "O2", "NaCl"]},
    {"q": "Sabse tez daudne wala jaanwar kaunsa hai?", "correct": "Cheetah", "wrong": ["Sher", "Ghoda", "Kutta"]},
    {"q": "Maanav sharir mein kitni haddiyan hoti hain?", "correct": "206", "wrong": ["200", "210", "250"]},
    {"q": "Surya se sabse nazdeek grah kaunsa hai?", "correct": "Mercury", "wrong": ["Earth", "Venus", "Mars"]},
    {"q": "Bijli ka aavishkar kisne kiya?", "correct": "Benjamin Franklin", "wrong": ["Newton", "Nikola Tesla", "Einstein"]},
    {"q": "Duniya ka sabse bada planet kaunsa hai?", "correct": "Jupiter", "wrong": ["Earth", "Saturn", "Neptune"]},
    {"q": "Vayu mein oxygen kitna pratishat hai?", "correct": "21%", "wrong": ["50%", "10%", "78%"]},
    {"q": "Light ki speed kitni hai?", "correct": "3 Lakh km/s", "wrong": ["1 Lakh km/s", "5 Lakh km/s", "10 Lakh km/s"]},
    {"q": "Duniya ka sabse chhota jeev kaunsa hai?", "correct": "Virus", "wrong": ["Bacteria", "Amoeba", "Fungi"]},
    {"q": "Khoon ka rang laal kyun hota hai?", "correct": "Iron", "wrong": ["Calcium", "Sodium", "Potassium"]},
    {"q": "Duniya ka sabse bada jeev kaunsa hai?", "correct": "Blue Whale", "wrong": ["Hathi", "Giraffe", "Shark"]},
    {"q": "Dharti ka ek chakkar pura karne mein kitna time lagta hai?", "correct": "24 hours", "wrong": ["12 hours", "48 hours", "30 days"]},
    {"q": "Photosynthesis mein kaunsi gas nikalti hai?", "correct": "Oxygen", "wrong": ["CO2", "Nitrogen", "Hydrogen"]},
    {"q": "Newton ka pehla niyam kya kehta hai?", "correct": "Inertia", "wrong": ["Force = Mass x Acceleration", "Action-Reaction", "Gravity"]},
    {"q": "Bijli ka SI unit kya hai?", "correct": "Ampere", "wrong": ["Volt", "Watt", "Ohm"]},
    {"q": "Sound ki speed sabse tez kahan hoti hai?", "correct": "Solid", "wrong": ["Liquid", "Gas", "Vacuum"]},
    {"q": "Aankh ka kaunsa hissa rang dekhta hai?", "correct": "Retina", "wrong": ["Cornea", "Iris", "Pupil"]},
    
    # Computer
    {"q": "HTML ka full form kya hai?", "correct": "Hyper Text Markup Language", "wrong": ["High Text Language", "Hyper Tabular", "Home Tool"]},
    {"q": "Computer ka dimaag kaunsa hai?", "correct": "CPU", "wrong": ["RAM", "Monitor", "Hard Disk"]},
    {"q": "JS mein 'getElementById' kya karta hai?", "correct": "Element dhundna", "wrong": ["File save karna", "Math karna", "Color badalna"]},
    {"q": "Windows 11 kis company ka hai?", "correct": "Microsoft", "wrong": ["Apple", "Google", "Linux"]},
    {"q": "1 KB mein kitne Bytes hote hain?", "correct": "1024", "wrong": ["1000", "512", "2048"]},
    {"q": "CSS ka kaam kya hai?", "correct": "Design karna", "wrong": ["Logic likhna", "Data save karna", "Server chalana"]},
    {"q": "Python kis type ki language hai?", "correct": "Programming", "wrong": ["Markup", "Database", "Hardware"]},
    {"q": "Pehla computer virus kab aaya?", "correct": "1971", "wrong": ["1981", "1991", "2001"]},
    {"q": "RAM ka full form kya hai?", "correct": "Random Access Memory", "wrong": ["Read Access Memory", "Real Action Memory", "Rapid Access Memory"]},
    {"q": "Computer ka father kise kaha jata hai?", "correct": "Charles Babbage", "wrong": ["Bill Gates", "Steve Jobs", "Mark Zuckerberg"]},
    {"q": "USB ka full form kya hai?", "correct": "Universal Serial Bus", "wrong": ["United Serial Bus", "Universal System Bus", "User Serial Bus"]},
    {"q": "Kaunsa storage sabse fast hai?", "correct": "SSD", "wrong": ["HDD", "DVD", "Pen Drive"]},
    {"q": "HTTP ka full form kya hai?", "correct": "Hyper Text Transfer Protocol", "wrong": ["Hyper Text Transmission Process", "High Text Transfer Protocol", "None"]},
    {"q": "Binary system mein kitne digits hote hain?", "correct": "2", "wrong": ["1", "4", "8"]},
    {"q": "Kaunsa component video output deta hai?", "correct": "GPU", "wrong": ["CPU", "RAM", "SSD"]},
    
    # History
    {"q": "Bharat ko azaadi kab mili?", "correct": "1947", "wrong": ["1945", "1950", "1942"]},
    {"q": "Taj Mahal kisne banwaya?", "correct": "Shah Jahan", "wrong": ["Akbar", "Babur", "Humayun"]},
    {"q": "Bharat ka pehla Pradhan Mantri kaun tha?", "correct": "Nehru", "wrong": ["Patel", "Gandhi", "Ambedkar"]},
    {"q": "Jhansi ki Rani ka naam kya tha?", "correct": "Lakshmi Bai", "wrong": ["Padmavati", "Razia Sultan", "Ahilya"]},
    {"q": "Mahabharat kisne likhi thi?", "correct": "Ved Vyas", "wrong": ["Valmiki", "Tulsidas", "Kalidas"]},
    {"q": "Dandi March kab hua tha?", "correct": "1930", "wrong": ["1942", "1920", "1919"]},
    {"q": "Mughal samrajya ka sansthapak kaun tha?", "correct": "Babur", "wrong": ["Akbar", "Humayun", "Shah Jahan"]},
    {"q": "Ashoka ne kis dharm ko apnaya?", "correct": "Buddhism", "wrong": ["Hindu", "Jain", "Sikh"]},
    {"q": "Kalinga Yudh kisne jeeta tha?", "correct": "Ashoka", "wrong": ["Chandragupta", "Samudragupta", "Harsha"]},
    {"q": "Bharat ka pehla rashtrapati kaun tha?", "correct": "Rajendra Prasad", "wrong": ["Nehru", "Radhakrishnan", "Zakir Hussain"]},
    {"q": "Indus Valley Civilization ka sabse bada sheher?", "correct": "Mohenjo-daro", "wrong": ["Harappa", "Lothal", "Dholavira"]},
    {"q": "1857 ki kranti ka main karan?", "correct": "Sipahi Vidroh", "wrong": ["Sanyukt Rashtriya Andolan", "Simon Commission", "Jallianwala"]},
    {"q": "Swami Vivekananda ne kaunsa bhashan diya?", "correct": "Chicago Speech", "wrong": ["Delhi Speech", "Lahore Speech", "None"]},
    {"q": "Chandragupta Maurya ke guru kaun the?", "correct": "Chanakya", "wrong": ["Buddha", "Mahavira", "Patanjali"]},
    {"q": "Jallianwala Bagh hatyakand kab hua?", "correct": "1919", "wrong": ["1920", "1930", "1942"]},
    
    # Sports
    {"q": "Cricket mein ek over mein kitni ball hoti hain?", "correct": "6", "wrong": ["4", "5", "8"]},
    {"q": "FIFA World Cup kitne saal mein ek baar hota hai?", "correct": "4", "wrong": ["2", "3", "5"]},
    {"q": "Bharat ka rashtriya khel kaunsa hai?", "correct": "Hockey", "wrong": ["Cricket", "Football", "Kabaddi"]},
    {"q": "Olympic Games kitne saal mein ek baar hote hain?", "correct": "4", "wrong": ["2", "3", "5"]},
    {"q": "Sachin Tendulkar ka nickname kya hai?", "correct": "God of Cricket", "wrong": ["Master Blaster", "Little Master", "Wall of India"]},
]

# Auto-generate extra math questions to ensure we have over 100 questions
for i in range(30):
    REAL_QUESTIONS.append({
        "q": f"Math: What is {i*12 + 5} + {i*7 + 10}?", 
        "correct": str((i*12 + 5) + (i*7 + 10)), 
        "wrong": [str((i*12 + 5) + (i*7 + 10) + 2), str((i*12 + 5) + (i*7 + 10) - 5), str((i*12 + 5) + (i*7 + 10) + 10)]
    })

def prepare_questions(category_pool):
    final_qs = []
    for idx, q_data in enumerate(category_pool):
        correct = q_data['correct']
        wrongs = q_data['wrong'][:]
        options = [correct] + wrongs
        random.shuffle(options)
        ans_idx = options.index(correct)
        
        q_id = f"q_{idx}_{random.randint(1000,9999)}"
        final_qs.append({
            "id": q_id,
            "q": q_data['q'],
            "options": options,
            "secure_ans": ans_idx
        })
    return final_qs

def generate_math_questions(num=16):
    questions = []
    for i in range(num):
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        op = random.choice(['+', '-', '*'])
        if op == '+': ans = a + b
        elif op == '-': ans = a - b
        else: ans = a * b
        correct_ans_str = str(ans)
        options = [correct_ans_str]
        while len(options) < 4:
            wrong = ans + random.randint(-20, 20)
            if str(wrong) not in options and wrong != ans:
                options.append(str(wrong))
        random.shuffle(options)
        ans_index = options.index(correct_ans_str)
        questions.append({
            "id": f"m{i}_{random.randint(1000,9999)}", 
            "q": f"Calculate: {a} {op} {b} = ?", 
            "options": options, 
            "secure_ans": ans_index
        })
    return questions

def generate_ai_questions(category):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Generate 16 multiple-choice questions for a quiz on the topic '{category}'. Provide the response STRICTLY as a JSON list of dictionaries. Each dictionary must have keys: 'q' (question string), 'options' (list of exactly 4 string choices), and 'ans' (integer index 0, 1, 2, or 3 for the correct option). Do not add any markdown formatting like ```json, just output the raw JSON array."
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(text)
        for i, q in enumerate(questions):
            q["id"] = f"ai_{random.randint(1000,9999)}_{i}"
            q["secure_ans"] = q["ans"]
            del q["ans"]
        return questions
    except Exception as e:
        return []

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>KBC Pro Ticket Edition</title>
  <link rel="manifest" href="/manifest.json">
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;600&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Teko', sans-serif; user-select: none; }
    body { background: #02040a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; background: radial-gradient(circle, #0a1128 0%, #000 100%); }
    
    .game-container {
      position: relative; width: 100%; max-width: 900px; height: 100vh; max-height: 850px;
      display: flex; background: rgba(5, 10, 31, 0.9); border: 2px solid #f1c40f; border-radius: 15px; overflow: hidden;
      box-shadow: 0 0 50px rgba(241, 196, 15, 0.3);
    }
    
    .main-area { flex: 1; position: relative; display: flex; flex-direction: column; padding: 15px; }
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .quit-btn { background: #e74c3c; color: white; border: none; padding: 8px 20px; border-radius: 20px; font-size: 18px; cursor: pointer; font-weight: bold; box-shadow: 0 0 10px #e74c3c; }
    
    .timer-circle {
      width: 65px; height: 65px; border-radius: 50%; display: flex; justify-content: center; align-items: center;
      font-size: 32px; font-weight: bold; color: #f1c40f; border: 3px solid #f1c40f;
      box-shadow: 0 0 15px rgba(241, 196, 15, 0.8), inset 0 0 10px rgba(241,196,15,0.5);
      animation: pulse 2s infinite alternate;
    }
    @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.05); } }
    
    .score-display {
      background: linear-gradient(90deg, #111, #1a2a6c, #111);
      border: 2px solid #f1c40f; border-radius: 15px;
      text-align: center; padding: 5px 10px; margin-bottom: 15px;
      box-shadow: 0 0 20px rgba(241, 196, 15, 0.4);
    }
    .score-display h3 { font-size: 22px; color: #fff; margin: 0; }
    .score-display .current-money { font-size: 32px; color: #2ecc71; font-weight: bold; text-shadow: 0 0 10px #2ecc71; }
    .score-display .next-target { font-size: 18px; color: #f1c40f; margin-top: -5px; }

    .lifelines { display: flex; gap: 15px; margin-bottom: 15px; }
    .lifeline-btn {
      width: 60px; height: 60px; border-radius: 50%; border: 2px solid #3498db;
      background: rgba(52, 152, 219, 0.2); color: #3498db; font-size: 20px; font-weight: bold;
      cursor: pointer; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: 0.3s;
      box-shadow: 0 0 15px rgba(52, 152, 219, 0.3);
    }
    .lifeline-btn span { font-size: 14px; color: #f1c40f; }
    .lifeline-btn:disabled { border-color: #444; color: #444; pointer-events: none; opacity: 0.3; box-shadow: none; }

    .quiz-area { flex: 1; display: flex; flex-direction: column; justify-content: center; }
    .question-box {
      background: linear-gradient(90deg, rgba(0,0,0,0.8), rgba(26, 42, 108, 0.8), rgba(0,0,0,0.8));
      border: 2px solid #f1c40f; border-radius: 50px; padding: 20px;
      text-align: center; font-size: 24px; line-height: 1.3; margin-bottom: 20px;
      box-shadow: 0 0 30px rgba(241, 196, 15, 0.3);
    }
    .options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .option {
      background: linear-gradient(90deg, #111, #1a1a1a); border: 2px solid #444;
      border-radius: 40px; padding: 12px 15px; font-size: 20px; cursor: pointer;
      display: flex; align-items: center; transition: 0.2s;
    }
    .option:hover { border-color: #f1c40f; background: #222; box-shadow: 0 0 15px #f1c40f; }
    .option span { color: #f1c40f; margin-right: 10px; font-weight: bold; font-size: 22px; }
    .option.correct { background: #2ecc71 !important; border-color: #fff; color: #000; box-shadow: 0 0 25px #2ecc71; }
    .option.wrong { background: #e74c3c !important; border-color: #fff; color: #fff; box-shadow: 0 0 25px #e74c3c; }
    .option.hidden { visibility: hidden; }

    .money-ladder {
      width: 200px; background: rgba(0,0,0,0.7); border-left: 2px solid #f1c40f;
      padding: 5px; display: flex; flex-direction: column-reverse; justify-content: flex-start;
      overflow-y: auto; box-shadow: -5px 0 20px rgba(0,0,0,0.8);
    }
    .ladder-item {
      font-size: 16px; padding: 4px 8px; color: #888; display: flex; justify-content: space-between;
      border-radius: 5px; margin-bottom: 2px; transition: 0.3s;
    }
    .ladder-item.active { color: #000; font-weight: bold; background: #f1c40f; transform: scale(1.05); box-shadow: 0 0 10px #f1c40f;}
    .ladder-item.milestone { color: #2ecc71; font-weight: bold; }
    .ladder-item.milestone.active { color: #000; background: #2ecc71; box-shadow: 0 0 10px #2ecc71;}

    .shake { animation: shake 0.5s; }
    @keyframes shake { 0% { transform: translate(1px, 1px) rotate(0deg); } 10% { transform: translate(-1px, -2px) rotate(-1deg); } 20% { transform: translate(-3px, 0px) rotate(1deg); } 30% { transform: translate(3px, 2px) rotate(0deg); } 40% { transform: translate(1px, -1px) rotate(1deg); } 50% { transform: translate(-1px, 2px) rotate(-1deg); } 60% { transform: translate(-3px, 1px) rotate(0deg); } 70% { transform: translate(3px, 1px) rotate(-1deg); } 80% { transform: translate(-1px, -1px) rotate(1deg); } 90% { transform: translate(1px, 2px) rotate(0deg); } 100% { transform: translate(1px, -2px) rotate(-1deg); } }

    .overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.95); display: flex; flex-direction: column; justify-content: center; align-items: center;
      z-index: 100; text-align: center; padding: 20px; backdrop-filter: blur(10px);
    }
    .overlay h2 { font-size: 50px; color: #f1c40f; margin-bottom: 10px; text-shadow: 0 0 20px #f1c40f; }
    .overlay p { font-size: 26px; margin-bottom: 20px; }
    .btn { padding: 15px 40px; font-size: 22px; background: #f1c40f; color: #000; border: none; border-radius: 30px; font-weight: bold; cursor: pointer; box-shadow: 0 0 20px rgba(241,196,15,0.6); margin: 10px; transition: 0.2s;}
    .btn:hover { transform: scale(1.05); }
    .btn-blue { background: #3498db; color: #fff; box-shadow: 0 0 20px rgba(52,152,219,0.6); }
    .btn-orange { background: #e67e22; color: #fff; box-shadow: 0 0 20px rgba(230,126,34,0.6); }
    .btn-red { background: #e74c3c; color: #fff; box-shadow: 0 0 20px rgba(231,76,60,0.6); }
    .btn:disabled { background: #555; color: #aaa; box-shadow: none; cursor: not-allowed; transform: none; }
    .hidden { display: none !important; }

    .shop-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; width: 100%; max-width: 600px; }
    .shop-card { background: #111; border: 2px solid #444; border-radius: 10px; padding: 15px; text-align: center; display: flex; flex-direction: column; justify-content: space-between;}

    .modal-box {
      background: #1a1a2e; border: 3px solid #e74c3c; border-radius: 20px; padding: 30px; text-align: center;
      box-shadow: 0 0 40px rgba(231, 76, 60, 0.5); max-width: 450px; width: 90%;
    }
    .modal-box h2 { color: #e74c3c; font-size: 40px; margin-bottom: 10px; }
    .modal-box p { font-size: 22px; color: #ccc; margin-bottom: 15px; }

    #adOverlay { background: #000; z-index: 200; display: none; }
    .ad-loader { width: 50px; height: 50px; border: 5px solid #333; border-top: 5px solid #f1c40f; border-radius: 50%; animation: spin 1s linear infinite; margin: 20px auto; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    #adTimerLarge { font-size: 80px; color: #fff; margin: 20px 0; font-weight: bold; }

    .ticket-icon { color: #f1c40f; text-shadow: 0 0 10px #f1c40f; font-size: 28px; }
    
    @media (max-width: 700px) {
      .money-ladder { display: none; }
      .options { grid-template-columns: 1fr; }
      .question-box { font-size: 20px; padding: 15px; }
      .option { font-size: 18px; padding: 10px 15px; }
      .shop-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <div class="game-container" id="gameContainer">
    
    <div class="overlay" id="menuScreen">
      <h2>KBC Pro Edition</h2>
      <div style="font-size: 24px; margin-bottom: 10px; display: flex; justify-content: center; gap: 20px;">
        <span>🪙 Coins: <b id="coinBalance" style="color:#f1c40f">0</b></span>
        <span class="ticket-icon">🎫 Tickets: <b id="ticketBalance" style="color:#f1c40f">0</b></span>
      </div>
      
      <div class="shop-grid">
        <div class="shop-card">
          <h3 style="color: #e67e22; font-size: 22px;">Earn Coins</h3>
          <p style="font-size: 14px; color: #aaa; margin-bottom: 10px;">Watch Ad -> +100 Coins</p>
          <button class="btn btn-orange" style="padding: 10px; font-size: 18px;" onclick="showAd('coins')">Watch Video</button>
        </div>
        <div class="shop-card">
          <h3 style="color: #f1c40f; font-size: 22px;">Buy Ticket</h3>
          <p style="font-size: 14px; color: #aaa; margin-bottom: 10px;">1 Ticket = 500 Coins</p>
          <button class="btn" style="padding: 10px; font-size: 18px;" onclick="buyTicketWithCoins()">Buy Ticket</button>
        </div>
        <div class="shop-card">
          <h3 style="color: #2ecc71; font-size: 22px;">Free Ticket</h3>
          <p style="font-size: 14px; color: #aaa; margin-bottom: 10px;">Watch Ad -> +1 Ticket</p>
          <button class="btn btn-blue" style="padding: 10px; font-size: 18px;" onclick="showAd('ticket')">Watch Video</button>
        </div>
        <div class="shop-card">
          <h3 style="color: #9b59b6; font-size: 22px;">Play Pro</h3>
          <p style="font-size: 14px; color: #aaa; margin-bottom: 10px;">Use 1 Ticket to play (₹7 Cr Prize)</p>
          <button class="btn" style="padding: 10px; font-size: 18px; background: #9b59b6; color: white;" onclick="startProGame()">Play Now</button>
        </div>
      </div>
    </div>

    <div class="overlay hidden" id="categoryScreen">
      <h2>Select Category</h2>
      <div class="shop-grid" id="categoryGrid"></div>
    </div>

    <div class="main-area hidden" id="mainGameArea">
      <div class="top-bar">
        <button class="quit-btn" id="quitBtn">Quit</button>
        <div class="timer-circle" id="timerDisplay">45</div>
      </div>

      <div class="score-display">
        <h3>Aapka Current Prize</h3>
        <div class="current-money" id="currentScore">₹ 0</div>
        <div class="next-target" id="nextTargetText">Next Target: ₹ 1,000</div>
      </div>

      <div class="lifelines">
        <button class="lifeline-btn" id="ll5050" onclick="useLifeline('5050')">50:50 <span id="count5050">0</span></button>
        <button class="lifeline-btn" id="llAudience" onclick="useLifeline('audience')">👥 <span id="countAudience">0</span></button>
        <button class="lifeline-btn" id="llPhone" onclick="useLifeline('phone')">📞 <span id="countPhone">0</span></button>
        <button class="lifeline-btn" id="llExpert" onclick="useLifeline('expert')" style="border-color: #9b59b6; color: #9b59b6; box-shadow: 0 0 15px rgba(155,89,182,0.3);">🧑‍🔬 <span id="countExpert">0</span></button>
      </div>

      <div class="quiz-area">
        <div class="question-box" id="questionText">Loading...</div>
        <div class="options" id="optionsContainer"></div>
      </div>
    </div>

    <div class="money-ladder hidden" id="moneyLadder"></div>

    <div class="overlay hidden" id="wrongScreen" style="background: rgba(0,0,0,0.85);">
      <div class="modal-box">
        <h2>❌ Galat Jawab!</h2>
        <p>Aapne abhi tak <b style="color:#2ecc71; font-size: 26px;" id="lostPrizeText">₹ 0</b> jeete hain!</p>
        <p style="color: #f1c40f; font-size: 18px;">Ad dekh kar apna ye prize bachayein!</p>
        
        <button class="btn btn-red" onclick="endGame('wrong')">Go to Home</button>
        <button class="btn btn-blue" id="reviveBtn" onclick="showAd('revive')">Watch Ad & Continue</button>
      </div>
    </div>

    <div class="overlay hidden" id="resultScreen">
      <h2 id="resultTitle">Game Over</h2>
      <p>Tumne jeete: <span id="finalMoney" style="color:#2ecc71">₹ 0</span></p>
      <button class="btn" onclick="goHome()">Back to Home</button>
    </div>

    <!-- IN-APP AD OVERLAY -->
    <div class="overlay" id="adOverlay">
      <h2 style="color: #fff;">Advertisement</h2>
      <div class="ad-loader"></div>
      <div id="adTimerLarge">15</div>
      <p style="color: #aaa;">Your reward is being prepared...</p>
      <button class="btn btn-blue" id="claimAdBtn" style="display: none;" onclick="claimAdReward()">Claim Reward</button>
    </div>

  </div>

  <script>
    let audioCtx;
    function initAudio() { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
    function playTone(freq, type, duration, vol=0.1) {
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
      osc.type = type; osc.frequency.value = freq;
      osc.connect(gain); gain.connect(audioCtx.destination);
      gain.gain.setValueAtTime(vol, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
      osc.start(); osc.stop(audioCtx.currentTime + duration);
    }
    const sounds = {
      correct: () => { playTone(800, 'sine', 0.1); setTimeout(()=>playTone(1000, 'sine', 0.3), 100); },
      wrong: () => playTone(150, 'sawtooth', 0.5, 0.3),
      win: () => { [400,500,600,800].forEach((f,i)=> setTimeout(()=>playTone(f,'sine',0.3), i*150)); }
    };

    const user = "player1";
    let userData = {};
    let gameQuestions = [];
    let currentQ = 0;
    let timeLeft = 45, timerInterval, canClick = false;
    let adActionType = ""; 
    let adInterval;
    
    const prizeMoney = [
      "₹ 1,000", "₹ 2,000", "₹ 3,000", "₹ 5,000", "₹ 10,000", 
      "₹ 20,000", "₹ 40,000", "₹ 80,000", "₹ 1,60,000", "₹ 3,20,000", 
      "₹ 6,40,000", "₹ 12,50,000", "₹ 25,00,000", "₹ 50,00,000", "₹ 1 CRORE", "₹ 7 CRORE"
    ];

    function fetchData() {
      fetch('/api/get_data/' + user)
        .then(res => res.json())
        .then(data => {
          userData = data;
          document.getElementById("coinBalance").innerText = data.coins;
          document.getElementById("ticketBalance").innerText = data.tickets;
          document.getElementById("count5050").innerText = data.lifelines["5050"];
          document.getElementById("countAudience").innerText = data.lifelines["audience"];
          document.getElementById("countPhone").innerText = data.lifelines["phone"];
          document.getElementById("countExpert").innerText = data.lifelines["expert"];
        });
    }

    function buildLadder() {
      let ladder = document.getElementById("moneyLadder");
      ladder.innerHTML = "";
      prizeMoney.forEach((amount, index) => {
        const div = document.createElement("div");
        div.className = "ladder-item";
        if ([4, 9, 14, 15].includes(index)) div.classList.add("milestone");
        div.innerHTML = `<span>${index + 1}</span> <span>${amount}</span>`;
        div.id = `ladder-${index}`;
        ladder.appendChild(div);
      });
    }

    // --- AD SYSTEM ---
    function showAd(action) {
      adActionType = action;
      
      // Adsterra Link Opens Here
      let videoLink = "https://asiafilm.org/4/23852721a9ede5c4d23ead1ed92dadc3"; 
      window.open(videoLink, '_blank');

      document.getElementById("adOverlay").style.display = "flex";
      document.getElementById("claimAdBtn").style.display = "none";
      document.getElementById("adTimerLarge").innerText = "15";
      
      let waitTime = 15;
      clearInterval(adInterval);
      adInterval = setInterval(() => {
        waitTime--;
        document.getElementById("adTimerLarge").innerText = waitTime;
        if (waitTime <= 0) {
          clearInterval(adInterval);
          document.getElementById("adTimerLarge").innerText = "0";
          document.getElementById("claimAdBtn").style.display = "block";
        }
      }, 1000);
    }

    function claimAdReward() {
      document.getElementById("adOverlay").style.display = "none";
      if (adActionType === 'revive') {
        document.getElementById("wrongScreen").classList.add("hidden");
        loadQuestion();
        return;
      }

      let endpoint = adActionType === 'coins' ? "/api/ad_reward_coins" : "/api/ad_reward_ticket";
      fetch(endpoint, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user}) })
      .then(res => res.json()).then(data => {
        fetchData();
      });
    }

    function buyTicketWithCoins() {
      if (userData.coins < 500) { alert("Tumhare paas 500 Coins nahi hain!"); return; }
      fetch('/api/buy_ticket', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user}) })
      .then(res => res.json()).then(data => {
        if(data.status === "success") {
          fetchData();
          if (typeof confetti === 'function') confetti({ particleCount: 50, spread: 60, origin: { y: 0.8 } });
        }
      });
    }

    function startProGame() {
      if (userData.tickets < 1) { alert("Tumhare paas Ticket nahi hai! Pehle ticket kharido ya ad dekho."); return; }
      fetch('/api/use_ticket', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user}) })
      .then(res => res.json()).then(data => {
        if(data.status === "success") {
          fetchData();
          document.getElementById("menuScreen").classList.add("hidden");
          document.getElementById("categoryScreen").classList.remove("hidden");
          showCategories();
        }
      });
    }

    function showCategories() {
      const grid = document.getElementById("categoryGrid");
      grid.innerHTML = "";
      const cats = ["Mix (All)", "Dynamic Math", "AI Generated (Infinite)"];
      
      cats.forEach(cat => {
        const btn = document.createElement("button");
        btn.className = "btn btn-blue"; btn.style.fontSize = "20px"; btn.innerText = cat;
        btn.onclick = () => startGame(cat);
        grid.appendChild(btn);
      });
    }

    function startGame(category) {
      fetch('/api/start_game', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: user, category: category})
      }).then(res => res.json()).then(data => {
        if(data.status === "success" && data.questions && data.questions.length > 0) {
          gameQuestions = data.questions;
          currentQ = 0;
          document.getElementById("categoryScreen").classList.add("hidden");
          document.getElementById("mainGameArea").classList.remove("hidden");
          document.getElementById("moneyLadder").classList.remove("hidden");
          buildLadder();
          initAudio();
          loadQuestion();
        } else {
          alert("Game data load nahi hua. Dobara try karein.");
        }
      });
    }

    function loadQuestion() {
      if (!gameQuestions || currentQ >= gameQuestions.length) { endGame("win"); return; }
      
      let q = gameQuestions[currentQ];
      if (!q) { endGame("win"); return; }

      canClick = true; timeLeft = 45;
      document.getElementById("timerDisplay").innerText = timeLeft;
      document.getElementById("timerDisplay").style.color = "#f1c40f";
      
      let currentWon = currentQ === 0 ? "₹ 0" : prizeMoney[currentQ - 1];
      document.getElementById("currentScore").innerText = currentWon;
      document.getElementById("nextTargetText").innerText = `Next Target: ${prizeMoney[currentQ]}`;

      document.getElementById("questionText").innerText = q.q;
      let optCont = document.getElementById("optionsContainer");
      optCont.innerHTML = "";
      
      document.querySelectorAll('.ladder-item').forEach(el => el.classList.remove('active'));
      document.getElementById(`ladder-${currentQ}`).classList.add('active');
      document.getElementById(`ladder-${currentQ}`).scrollIntoView({ behavior: 'smooth', block: 'center' });

      const letters = ["A", "B", "C", "D"];
      q.options.forEach((opt, i) => {
        const div = document.createElement("div");
        div.className = "option";
        div.id = "opt-" + i;
        div.innerHTML = `<span>${letters[i]}.</span> ${opt}`;
        div.onclick = () => checkAnswerServer(i, div, q.id);
        optCont.appendChild(div);
      });

      clearInterval(timerInterval);
      timerInterval = setInterval(() => {
        timeLeft--;
        document.getElementById("timerDisplay").innerText = timeLeft;
        if (timeLeft <= 10) document.getElementById("timerDisplay").style.color = "#e74c3c";
        if (timeLeft <= 0) { clearInterval(timerInterval); showWrongPopup(); }
      }, 1000);
    }

    function checkAnswerServer(selectedIdx, el, qId) {
      if (!canClick) return;
      canClick = false; clearInterval(timerInterval);
      
      fetch('/api/check_answer', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: user, question_id: qId, selected_idx: selectedIdx})
      }).then(res => res.json()).then(data => {
          if(data.is_correct) {
            el.classList.add("correct"); sounds.correct();
            if (typeof confetti === 'function') confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
            setTimeout(() => { currentQ++; loadQuestion(); }, 1500);
          } else {
            el.classList.add("wrong"); sounds.wrong();
            let gContainer = document.getElementById("gameContainer");
            gContainer.classList.add("shake");
            setTimeout(() => gContainer.classList.remove("shake"), 500);
            
            if(data.correct_idx !== undefined) {
                setTimeout(() => document.getElementById("opt-" + data.correct_idx).classList.add("correct"), 500);
            }
            setTimeout(() => showWrongPopup(), 1500);
          }
      });
    }

    function showWrongPopup() {
      canClick = false;
      let currentWon = currentQ === 0 ? "₹ 0" : prizeMoney[currentQ - 1];
      document.getElementById("lostPrizeText").innerText = currentWon;
      document.getElementById("wrongScreen").classList.remove("hidden");
      document.getElementById("reviveBtn").disabled = false;
    }

    function useLifeline(type) {
      if (userData.lifelines[type] <= 0) { alert("Lifeline khatam! Pehle kharido."); return; }
      if (!canClick) return;

      fetch('/api/use_lifeline', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: user, type: type, question_id: gameQuestions[currentQ].id})
      }).then(res => res.json()).then(data => {
        if (data.status === "success") {
          fetchData();
          if (type === '5050') {
            data.wrong_indices.forEach(idx => {
                document.getElementById("opt-" + idx).classList.add("hidden");
            });
          } else if (type === 'audience') {
            alert(`Audience Poll:\\nOption ${data.correct_idx} ko sabse zyada (60%) votes mile hain!`);
          } else if (type === 'phone') {
            alert(`Friend bolta hai: "Mujhe lagta hai sahi jawab Option ${data.correct_idx} hai!"`);
          } else if (type === 'expert') {
            alert(`🧑‍🔬 Expert bolta hai: "100% guarantee ke sath, sahi jawab Option ${data.correct_idx} hi hai."`);
          }
        }
      });
    }

    document.getElementById("quitBtn").onclick = () => { if (confirm("Quit karke paise lekar jao?")) endGame("quit"); };

    function endGame(reason) {
      canClick = false; clearInterval(timerInterval);
      document.getElementById("mainGameArea").classList.add("hidden");
      document.getElementById("moneyLadder").classList.add("hidden");
      document.getElementById("wrongScreen").classList.add("hidden");
      document.getElementById("resultScreen").classList.remove("hidden");
      
      let wonMoney = currentQ === 0 ? "₹ 0" : prizeMoney[currentQ - 1];
      let title = document.getElementById("resultTitle");
      
      if (reason === "win") { title.innerText = "🏆 CHAMPION!"; title.style.color = "#2ecc71"; document.getElementById("finalMoney").innerText = prizeMoney[prizeMoney.length - 1]; sounds.win(); }
      else if (reason === "quit") { title.innerText = "Farmaish!"; title.style.color = "#f1c40f"; document.getElementById("finalMoney").innerText = wonMoney; }
      else { title.innerText = "❌ GAME OVER!"; title.style.color = "#e74c3c"; document.getElementById("finalMoney").innerText = wonMoney; }
    }

    function goHome() {
      document.getElementById("resultScreen").classList.add("hidden");
      document.getElementById("menuScreen").classList.remove("hidden");
      fetchData();
    }

    window.onload = () => { fetchData(); buildLadder(); };
  </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_CODE)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "KBC Pro Game",
        "short_name": "KBC Pro",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#02040a",
        "theme_color": "#f1c40f",
        "description": "Play KBC Pro and win tickets!",
        "icons": [{"src": "https://raw.githubusercontent.com/ayannuman800-del/kbc-game/main/1794342592618.png", "sizes": "512x512", "type": "image/png"}]
    })

@app.route('/api/get_data/<username>', methods=['GET'])
def get_data(username):
    if username in users: return jsonify(users[username])
    return jsonify({"status": "error"})

@app.route('/api/buy_ticket', methods=['POST'])
def buy_ticket():
    username = request.json.get('username')
    if username in users and users[username]["coins"] >= 500:
        users[username]["coins"] -= 500
        users[username]["tickets"] += 1
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/api/use_ticket', methods=['POST'])
def use_ticket():
    username = request.json.get('username')
    if username in users and users[username]["tickets"] >= 1:
        users[username]["tickets"] -= 1
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/api/ad_reward_coins', methods=['POST'])
def ad_reward_coins():
    username = request.json.get('username')
    if username in users:
        users[username]["coins"] += 100
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/api/ad_reward_ticket', methods=['POST'])
def ad_reward_ticket():
    username = request.json.get('username')
    if username in users:
        users[username]["tickets"] += 1
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.json
    username = data.get('username')
    category = data.get('category')
    
    if username not in users: return jsonify({"status": "error"})

    final_secure_list = []
    if category == "Dynamic Math":
        final_secure_list = generate_math_questions(16)
    elif category == "AI Generated (Infinite)":
         final_secure_list = generate_ai_questions("General Knowledge")
         if not final_secure_list or len(final_secure_list) == 0: 
             final_secure_list = generate_math_questions(16)
    else:
        # FIXED: Simple and bug-free sample extraction
        pool = prepare_questions(REAL_QUESTIONS)
        final_secure_list = random.sample(pool, min(16, len(pool)))

    # Clean for frontend
    clean_qs = []
    game_ans = {}
    for q in final_secure_list:
        game_ans[q["id"]] = q["secure_ans"]
        clean_qs.append({"id": q["id"], "q": q["q"], "options": q["options"]})
    
    active_game_answers[username] = game_ans
    return jsonify({"status": "success", "questions": clean_qs})

@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    username = data.get('username')
    q_id = data.get('question_id')
    selected_idx = data.get('selected_idx')

    if username in active_game_answers and q_id in active_game_answers[username]:
        correct_idx = active_game_answers[username][q_id]
        is_correct = (selected_idx == correct_idx)
        return jsonify({"status": "success", "is_correct": is_correct, "correct_idx": correct_idx})
    
    return jsonify({"status": "error", "is_correct": False})

@app.route('/api/use_lifeline', methods=['POST'])
def use_lifeline():
    data = request.json
    username = data.get('username')
    life_type = data.get('type')
    q_id = data.get('question_id')

    if username in users and users[username]["lifelines"][life_type] > 0:
        users[username]["lifelines"][life_type] -= 1
        
        if username in active_game_answers and q_id in active_game_answers[username]:
            correct_idx = active_game_answers[username][q_id]
            wrong_indices = [0,1,2,3]
            wrong_indices.remove(correct_idx)
            random.shuffle(wrong_indices)
            
            return jsonify({
                "status": "success", 
                "correct_idx": correct_idx, 
                "wrong_indices": wrong_indices[:2]
            })
            
    return jsonify({"status": "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
