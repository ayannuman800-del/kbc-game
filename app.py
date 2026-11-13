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
        "lifelines": {"5050": 1, "audience": 1, "phone": 1, "expert": 1},
        "seen_questions": []
    } 
}

# --- MASTER QUESTION BANK (Real Questions) ---
REAL_QUESTIONS = {
    "General Knowledge": [
        {"q": "Bharat ki rajdhani kya hai?", "correct": "New Delhi", "wrong": ["Mumbai", "Kolkata", "Chennai"]},
        {"q": "Sabse bada mahasagar kaunsa hai?", "correct": "Pacific Ocean", "wrong": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]},
        {"q": "Bharat ka rashtriya pakshi kaunsa hai?", "correct": "Mor", "wrong": ["Kauwa", "Tota", "Kabootar"]},
        {"q": "Duniya ka sabse uncha parvat kaunsa hai?", "correct": "Mount Everest", "wrong": ["K2", "Kanchenjunga", "Makalu"]},
        {"q": "Bharat mein kitne rajya hain?", "correct": "28", "wrong": ["27", "29", "30"]},
        {"q": "Japan ki currency kya hai?", "correct": "Yen", "wrong": ["Yuan", "Won", "Dollar"]},
        {"q": "Duniya ka sabse bada desert kaunsa hai?", "correct": "Sahara", "wrong": ["Thar", "Gobi", "Antarctic"]},
        {"q": "Bharat ka rashtriya pashu kaunsa hai?", "correct": "Bagh", "wrong": ["Sher", "Hathi", "Gaay"]},
        {"q": "Sabse lambi nadi kaunsi hai?", "correct": "Nile", "wrong": ["Ganga", "Amazon", "Yamuna"]},
        {"q": "Australia ki rajdhani kya hai?", "correct": "Canberra", "wrong": ["Sydney", "Melbourne", "Perth"]}
    ],
    "Science": [
        {"q": "Pani ka rasayanik sutra kya hai?", "correct": "H2O", "wrong": ["CO2", "O2", "NaCl"]},
        {"q": "Sabse tez daudne wala jaanwar kaunsa hai?", "correct": "Cheetah", "wrong": ["Sher", "Ghoda", "Kutta"]},
        {"q": "Maanav sharir mein kitni haddiyan hoti hain?", "correct": "206", "wrong": ["200", "210", "250"]},
        {"q": "Surya se sabse nazdeek grah kaunsa hai?", "correct": "Mercury", "wrong": ["Earth", "Venus", "Mars"]},
        {"q": "Bijli ka aavishkar kisne kiya?", "correct": "Benjamin Franklin", "wrong": ["Newton", "Nikola Tesla", "Einstein"]},
        {"q": "Duniya ka sabse bada planet kaunsa hai?", "correct": "Jupiter", "wrong": ["Earth", "Saturn", "Neptune"]},
        {"q": "Vayu mein oxygen kitna pratishat hai?", "correct": "21%", "wrong": ["50%", "10%", "78%"]},
        {"q": "Light ki speed kitni hai?", "correct": "3 Lakh km/s", "wrong": ["1 Lakh km/s", "5 Lakh km/s", "10 Lakh km/s"]},
        {"q": "Duniya ka sabse chhota jeev kaunsa hai?", "correct": "Virus", "wrong": ["Bacteria", "Amoeba", "Fungi"]},
        {"q": "Khoon ka rang laal kyun hota hai?", "correct": "Iron", "wrong": ["Calcium", "Sodium", "Potassium"]}
    ],
    "Computer": [
        {"q": "HTML ka full form kya hai?", "correct": "Hyper Text Markup Language", "wrong": ["High Text Language", "Hyper Tabular", "Home Tool"]},
        {"q": "Computer ka dimaag kaunsa hai?", "correct": "CPU", "wrong": ["RAM", "Monitor", "Hard Disk"]},
        {"q": "JS mein 'getElementById' kya karta hai?", "correct": "Element dhundna", "wrong": ["File save karna", "Math karna", "Color badalna"]},
        {"q": "Windows 11 kis company ka hai?", "correct": "Microsoft", "wrong": ["Apple", "Google", "Linux"]},
        {"q": "1 KB mein kitne Bytes hote hain?", "correct": "1024", "wrong": ["1000", "512", "2048"]},
        {"q": "CSS ka kaam kya hai?", "correct": "Design karna", "wrong": ["Logic likhna", "Data save karna", "Server chalana"]},
        {"q": "Python kis type ki language hai?", "correct": "Programming", "wrong": ["Markup", "Database", "Hardware"]},
        {"q": "Pehla computer virus kab aaya?", "correct": "1971", "wrong": ["1981", "1991", "2001"]},
        {"q": "RAM ka full form kya hai?", "correct": "Random Access Memory", "wrong": ["Read Access Memory", "Real Action Memory", "Rapid Access Memory"]},
        {"q": "Computer ka father kise kaha jata hai?", "correct": "Charles Babbage", "wrong": ["Bill Gates", "Steve Jobs", "Mark Zuckerberg"]}
    ],
    "History": [
        {"q": "Bharat ko azaadi kab mili?", "correct": "1947", "wrong": ["1945", "1950", "1942"]},
        {"q": "Taj Mahal kisne banwaya?", "correct": "Shah Jahan", "wrong": ["Akbar", "Babur", "Humayun"]},
        {"q": "Bharat ka pehla Pradhan Mantri kaun tha?", "correct": "Nehru", "wrong": ["Patel", "Gandhi", "Ambedkar"]},
        {"q": "Jhansi ki Rani ka naam kya tha?", "correct": "Lakshmi Bai", "wrong": ["Padmavati", "Razia Sultan", "Ahilya"]},
        {"q": "Mahabharat kisne likhi thi?", "correct": "Ved Vyas", "wrong": ["Valmiki", "Tulsidas", "Kalidas"]},
        {"q": "Dandi March kab hua tha?", "correct": "1930", "wrong": ["1942", "1920", "1919"]},
        {"q": "Mughal samrajya ka sansthapak kaun tha?", "correct": "Babur", "wrong": ["Akbar", "Humayun", "Shah Jahan"]},
        {"q": "Ashoka ne kis dharm ko apnaya?", "correct": "Buddhism", "wrong": ["Hindu", "Jain", "Sikh"]},
        {"q": "Kalinga Yudh kisne jeeta tha?", "correct": "Ashoka", "wrong": ["Chandragupta", "Samudragupta", "Harsha"]},
        {"q": "Bharat ka pehla rashtrapati kaun tha?", "correct": "Rajendra Prasad", "wrong": ["Nehru", "Radhakrishnan", "Zakir Hussain"]}
    ]
}

# --- OPTIONS SHUFFLER (To ensure correct answer is random A,B,C,D) ---
def prepare_questions(category_pool):
    final_qs = []
    for q_data in category_pool:
        correct = q_data['correct']
        wrongs = q_data['wrong'][:]
        
        options = [correct] + wrongs
        random.shuffle(options) # Shuffles options randomly
        
        ans_idx = options.index(correct)
        final_qs.append({
            "q": q_data['q'],
            "options": options,
            "ans": ans_idx
        })
    return final_qs

ALL_QUESTIONS = {
    "General Knowledge": prepare_questions(REAL_QUESTIONS["General Knowledge"]),
    "Science": prepare_questions(REAL_QUESTIONS["Science"]),
    "Computer": prepare_questions(REAL_QUESTIONS["Computer"]),
    "History": prepare_questions(REAL_QUESTIONS["History"])
}
ALL_QUESTIONS["Mix (All)"] = ALL_QUESTIONS["General Knowledge"] + ALL_QUESTIONS["Science"] + ALL_QUESTIONS["Computer"] + ALL_QUESTIONS["History"]

# --- DYNAMIC MATH ---
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
        questions.append({"id": f"m{i}_{random.randint(1000,9999)}", "q": f"Calculate: {a} {op} {b} = ?", "options": options, "ans": ans_index})
    return questions

# --- AI GENERATOR ---
def generate_ai_questions(category):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Generate 16 multiple-choice questions for a quiz on the topic '{category}'. Provide the response STRICTLY as a JSON list of dictionaries. Each dictionary must have keys: 'q' (question string), 'options' (list of exactly 4 string choices), and 'ans' (integer index 0, 1, 2, or 3 for the correct option). Do not add any markdown formatting like ```json, just output the raw JSON array."
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(text)
        for i, q in enumerate(questions):
            q["id"] = f"ai_{random.randint(1000,9999)}_{i}"
        return questions
    except Exception as e:
        return []

# --- FRONTEND ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>KBC 7 Crore Edition</title>
  <link rel="manifest" href="/manifest.json">
  <!-- Canvas Confetti Library -->
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

    /* Shake Animation */
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

    .shop-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; width: 100%; max-width: 500px; }
    .shop-card { background: #111; border: 2px solid #444; border-radius: 10px; padding: 15px; text-align: center; }

    .modal-box {
      background: #1a1a2e; border: 3px solid #e74c3c; border-radius: 20px; padding: 30px; text-align: center;
      box-shadow: 0 0 40px rgba(231, 76, 60, 0.5); max-width: 450px; width: 90%;
    }
    .modal-box h2 { color: #e74c3c; font-size: 40px; margin-bottom: 10px; }
    .modal-box p { font-size: 22px; color: #ccc; margin-bottom: 15px; }
    
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
      <h2>KBC 7 Crore Edition</h2>
      <div style="font-size: 24px; margin-bottom: 10px;">🪙 Coins: <b id="coinBalance" style="color:#f1c40f">0</b></div>
      
      <div class="shop-grid">
        <div class="shop-card">
          <h3 style="color: #e67e22; font-size: 24px;">Watch Ad</h3>
          <p style="font-size: 16px; color: #aaa; margin-bottom: 10px;">Get 100 Coins + 1 Lifeline</p>
          <button class="btn btn-orange" style="padding: 10px 20px; font-size: 18px;" onclick="watchAd()">Watch Video</button>
        </div>
        <div class="shop-card">
          <h3 style="color: #3498db; font-size: 24px;">Buy Lifeline</h3>
          <p style="font-size: 16px; color: #aaa; margin-bottom: 10px;">Cost: 150 Coins</p>
          <button class="btn btn-blue" style="padding: 10px 20px; font-size: 18px;" onclick="buyLifeline()">Buy Random</button>
        </div>
      </div>
      
      <button class="btn" style="margin-top: 30px;" onclick="showCategories()">Play KBC</button>
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
        
        <!-- Ad Timer Display -->
        <h1 id="adTimerDisplay" style="color: #fff; font-size: 60px; margin: 10px 0; display: none;">60</h1>
        
        <button class="btn btn-red" onclick="endGame('wrong')">Go to Home</button>
        <button class="btn btn-blue" id="reviveBtn" onclick="reviveGame()">Watch Ad & Continue</button>
        <p id="adWaitText" style="font-size: 18px; color: #f1c40f; margin-top: 15px;"></p>
      </div>
    </div>

    <div class="overlay hidden" id="resultScreen">
      <h2 id="resultTitle">Game Over</h2>
      <p>Tumne jeete: <span id="finalMoney" style="color:#2ecc71">₹ 0</span></p>
      <button class="btn" onclick="goHome()">Back to Home</button>
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

    function watchAd() {
      let videoLink = "https://asiafilm.org/4/23852721a9ede5c4d23ead1ed92dadc3"; 
      alert("Video khul rahi hai. 10 second baad wapas aana.");
      window.open(videoLink, '_blank');

      setTimeout(() => {
        fetch('/api/ad_reward', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user}) })
        .then(res => res.json()).then(data => {
          alert("Shukriya! Tumhe 100 Coins aur 1 Lifeline mil gayi.");
          fetchData();
        });
      }, 10000);
    }

    function buyLifeline() {
      fetch('/api/buy_lifeline', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user}) })
      .then(res => res.json()).then(data => {
        if(data.status === "success") { alert("Lifeline kharid li gayi!"); fetchData(); }
        else { alert("Tumhare paas 150 Coins nahi hain!"); }
      });
    }

    function showCategories() {
      document.getElementById("menuScreen").classList.add("hidden");
      document.getElementById("categoryScreen").classList.remove("hidden");
      const grid = document.getElementById("categoryGrid");
      grid.innerHTML = "";
      const cats = ["Computer", "General Knowledge", "Science", "History", "Mix (All)", "Dynamic Math", "AI Generated (Infinite)"];
      
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
        if(data.status === "success") {
          gameQuestions = data.questions;
          currentQ = 0;
          document.getElementById("categoryScreen").classList.add("hidden");
          document.getElementById("mainGameArea").classList.remove("hidden");
          document.getElementById("moneyLadder").classList.remove("hidden");
          buildLadder();
          initAudio();
          loadQuestion();
        } else {
          alert("Kuch error aaya hai. Dobara try karo.");
        }
      });
    }

    function loadQuestion() {
      if (currentQ >= gameQuestions.length) { endGame("win"); return; }
      
      canClick = true; timeLeft = 45;
      document.getElementById("timerDisplay").innerText = timeLeft;
      document.getElementById("timerDisplay").style.color = "#f1c40f";
      
      let currentWon = currentQ === 0 ? "₹ 0" : prizeMoney[currentQ - 1];
      document.getElementById("currentScore").innerText = currentWon;
      document.getElementById("nextTargetText").innerText = `Next Target: ${prizeMoney[currentQ]}`;

      let q = gameQuestions[currentQ];
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
        div.onclick = () => checkAnswer(i, div);
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

    function checkAnswer(selected, el) {
      if (!canClick) return;
      canClick = false; clearInterval(timerInterval);
      
      let q = gameQuestions[currentQ];
      if (selected === q.ans) {
        el.classList.add("correct"); sounds.correct();
        
        // CONFETTI ANIMATION
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });

        setTimeout(() => { currentQ++; loadQuestion(); }, 1500);
      } else {
        el.classList.add("wrong"); sounds.wrong();
        document.getElementById("gameContainer").classList.add("shake");
        setTimeout(() => document.getElementById("gameContainer").classList.remove("shake"), 500);
        setTimeout(() => document.getElementById("opt-" + q.ans).classList.add("correct"), 500);
        setTimeout(() => showWrongPopup(), 1500);
      }
    }

    function showWrongPopup() {
      canClick = false;
      let currentWon = currentQ === 0 ? "₹ 0" : prizeMoney[currentQ - 1];
      document.getElementById("lostPrizeText").innerText = currentWon;
      
      document.getElementById("wrongScreen").classList.remove("hidden");
      let btn = document.getElementById("reviveBtn");
      btn.disabled = false;
      btn.innerText = "Watch Ad & Continue";
      document.getElementById("adWaitText").innerText = "";
      document.getElementById("adTimerDisplay").style.display = "none";
      
      // Reset button action
      btn.onclick = reviveGame;
    }

    function reviveGame() {
      let videoLink = "https://asiafilm.org/4/23852721a9ede5c4d23ead1ed92dadc3"; 
      window.open(videoLink, '_blank');
      
      let btn = document.getElementById("reviveBtn");
      let timerDisplay = document.getElementById("adTimerDisplay");
      btn.disabled = true;
      
      // AD TIMER SET TO 60 SECONDS (Change this to 30 or 45 if needed)
      let waitTime = 60; 
      timerDisplay.style.display = "block";
      timerDisplay.innerText = waitTime;
      document.getElementById("adWaitText").innerText = `Ad dekh rahe hain, kripya wait karein...`;

      let adTimer = setInterval(() => {
        waitTime--;
        timerDisplay.innerText = waitTime;
        
        if (waitTime <= 0) {
          clearInterval(adTimer);
          timerDisplay.style.display = "none";
          document.getElementById("adWaitText").innerText = "✅ Ad pura ho gaya! Ab aap continue kar sakte hain.";
          btn.disabled = false;
          btn.innerText = "Continue Game";
          btn.onclick = () => {
            document.getElementById("wrongScreen").classList.add("hidden");
            loadQuestion(); 
          };
        }
      }, 1000);
    }

    function useLifeline(type) {
      if (userData.lifelines[type] <= 0) { alert("Lifeline khatam! Pehle kharido."); return; }
      if (!canClick) return;

      fetch('/api/use_lifeline', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: user, type: type})
      }).then(res => res.json()).then(data => {
        if (data.status === "success") {
          fetchData();
          let q = gameQuestions[currentQ];
          
          if (type === '5050') {
            let wrongs = [0,1,2,3].filter(i => i !== q.ans).sort(() => 0.5 - Math.random());
            document.getElementById("opt-" + wrongs[0]).classList.add("hidden");
            document.getElementById("opt-" + wrongs[1]).classList.add("hidden");
          } else if (type === 'audience') {
            alert(`Audience Poll:\nOption ${q.ans} ko sabse zyada (60%) votes mile hain!`);
          } else if (type === 'phone') {
            alert(`Friend bolta hai: "Mujhe lagta hai sahi jawab Option ${q.ans} hai!"`);
          } else if (type === 'expert') {
            alert(`🧑‍🔬 Expert bolta hai: "100% guarantee ke sath, sahi jawab Option ${q.ans} hi hai."`);
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

# --- BACKEND API ROUTES ---
@app.route('/')
def home(): return render_template_string(HTML_CODE)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "KBC Game",
        "short_name": "KBC Game",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#02040a",
        "theme_color": "#f1c40f",
        "description": "Play KBC Quiz and win coins!",
        "icons": [
            {
                "src": "https://raw.githubusercontent.com/ayannuman800-del/kbc-game/main/1794342592618.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })

@app.route('/api/get_data/<username>', methods=['GET'])
def get_data(username):
    if username in users: return jsonify(users[username])
    return jsonify({"status": "error"})

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.json
    username = data.get('username')
    category = data.get('category')
    
    if username not in users: return jsonify({"status": "error"})

    if category == "AI Generated (Infinite)":
        ai_qs = generate_ai_questions("Computer, Science, History, or General Knowledge")
        if ai_qs and len(ai_qs) > 0:
            return jsonify({"status": "success", "questions": ai_qs})
        else:
            category = "Mix (All)"

    if category == "Dynamic Math":
        final_questions = generate_math_questions(16)
        return jsonify({"status": "success", "questions": final_questions})

    seen_ids = users[username]["seen_questions"]
    category_pool = ALL_QUESTIONS.get(category, ALL_QUESTIONS["Mix (All)"])
    
    new_pool = [q for q in category_pool if q["id"] not in seen_ids]
    old_pool = [q for q in category_pool if q["id"] in seen_ids]

    num_new_needed = int(16 * 0.8) 
    num_old_needed = 16 - num_new_needed 

    if len(new_pool) < num_new_needed:
        num_old_needed += (num_new_needed - len(new_pool))
        num_new_needed = len(new_pool)

    selected_new = random.sample(new_pool, num_new_needed) if new_pool else []
    selected_old = random.sample(old_pool, min(num_old_needed, len(old_pool))) if old_pool else []
    
    final_questions = selected_new + selected_old
    
    if len(final_questions) < 16:
        remaining = [q for q in category_pool if q not in final_questions]
        final_questions += random.sample(remaining, min(16 - len(final_questions), len(remaining)))

    random.shuffle(final_questions)

    for q in selected_new:
        if q["id"] not in users[username]["seen_questions"]:
            users[username]["seen_questions"].append(q["id"])

    if len(users[username]["seen_questions"]) > 100:
        users[username]["seen_questions"] = users[username]["seen_questions"][-100:]

    return jsonify({"status": "success", "questions": final_questions})

@app.route('/api/ad_reward', methods=['POST'])
def ad_reward():
    username = request.json.get('username')
    if username in users:
        users[username]["coins"] += 100
        random_life = random.choice(["5050", "audience", "phone", "expert"])
        users[username]["lifelines"][random_life] += 1
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/api/buy_lifeline', methods=['POST'])
def buy_lifeline():
    username = request.json.get('username')
    if username in users and users[username]["coins"] >= 150:
        users[username]["coins"] -= 150
        random_life = random.choice(["5050", "audience", "phone", "expert"])
        users[username]["lifelines"][random_life] += 1
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/api/use_lifeline', methods=['POST'])
def use_lifeline():
    data = request.json
    username, life_type = data.get('username'), data.get('type')
    if username in users and users[username]["lifelines"][life_type] > 0:
        users[username]["lifelines"][life_type] -= 1
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
