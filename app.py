
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# --- DATABASE (User ka hisaab) ---
users = {
    "player1": {
        "coins": 200, 
        "lifelines": {"5050": 1, "audience": 1, "phone": 1, "expert": 1},
        "seen_questions": []
    } 
}

# --- MASTER QUESTION BANK (Har sawal mein 4 Options hain!) ---
ALL_QUESTIONS = {
    "Computer": [
        {"id": "c1", "q": "HTML ka full form kya hai?", "options": ["Hyper Text Markup Language", "High Text Language", "Hyper Tabular", "Home Tool Markup"], "ans": 0},
        {"id": "c2", "q": "Computer ka dimaag kaunsa hai?", "options": ["RAM", "CPU", "Monitor", "Hard Disk"], "ans": 1},
        {"id": "c3", "q": "JS mein 'getElementById' kya karta hai?", "options": ["Element dhundna", "File save karna", "Math karna", "Color badalna"], "ans": 0},
        {"id": "c4", "q": "Windows 11 kis company ka OS hai?", "options": ["Apple", "Google", "Microsoft", "Linux"], "ans": 2},
        {"id": "c5", "q": "1 KB mein kitne Bytes hote hain?", "options": ["1024", "1000", "512", "2048"], "ans": 0},
        {"id": "c6", "q": "CSS ka kaam kya hai?", "options": ["Design karna", "Logic likhna", "Data save karna", "Server chalana"], "ans": 0},
        {"id": "c7", "q": "Python kis type ki language hai?", "options": ["Programming", "Markup", "Database", "Hardware"], "ans": 0},
        {"id": "c8", "q": "Sabse pehla computer virus kab aaya?", "options": ["1971", "1981", "1991", "2001"], "ans": 0},
        {"id": "c9", "q": "RAM ka full form kya hai?", "options": ["Random Access Memory", "Read Access Memory", "Real Action Memory", "Rapid Access Memory"], "ans": 0},
        {"id": "c10", "q": "Computer ka father kise kaha jata hai?", "options": ["Bill Gates", "Charles Babbage", "Steve Jobs", "Mark Zuckerberg"], "ans": 1}
    ],
    "General Knowledge": [
        {"id": "g1", "q": "Bharat ki rajdhani kya hai?", "options": ["Mumbai", "New Delhi", "Kolkata", "Chennai"], "ans": 1},
        {"id": "g2", "q": "Sabse bada mahasagar kaunsa hai?", "options": ["Atlantic", "Indian", "Pacific", "Arctic"], "ans": 2},
        {"id": "g3", "q": "Bharat ka rashtriya pakshi kaunsa hai?", "options": ["Kauwa", "Mor", "Tota", "Kabootar"], "ans": 1},
        {"id": "g4", "q": "Australia ki rajdhani kya hai?", "options": ["Sydney", "Canberra", "Melbourne", "Perth"], "ans": 1},
        {"id": "g5", "q": "Duniya ka sabse uncha parvat kaunsa hai?", "options": ["K2", "Mount Everest", "Kanchenjunga", "Makalu"], "ans": 1},
        {"id": "g6", "q": "Bharat mein kitne rajya hain?", "options": ["27", "28", "29", "30"], "ans": 1},
        {"id": "g7", "q": "Japan ki currency kya hai?", "options": ["Yuan", "Yen", "Won", "Dollar"], "ans": 1},
        {"id": "g8", "q": "Duniya ka sabse bada desert kaunsa hai?", "options": ["Sahara", "Thar", "Gobi", "Antarctic"], "ans": 0},
        {"id": "g9", "q": "Bharat ka rashtriya pashu kaunsa hai?", "options": ["Sher", "Bagh", "Hathi", "Gaay"], "ans": 1},
        {"id": "g10", "q": "Sabse lambi nadi kaunsi hai?", "options": ["Ganga", "Amazon", "Nile", "Yamuna"], "ans": 2}
    ],
    "Science": [
        {"id": "s1", "q": "Pani ka rasayanik sutra kya hai?", "options": ["CO2", "H2O", "O2", "NaCl"], "ans": 1},
        {"id": "s2", "q": "Sabse tez daudne wala jaanwar kaunsa hai?", "options": ["Sher", "Cheetah", "Ghoda", "Kutta"], "ans": 1},
        {"id": "s3", "q": "Maanav sharir mein kitni haddiyan hoti hain?", "options": ["200", "206", "210", "250"], "ans": 1},
        {"id": "s4", "q": "Surya se sabse nazdeek grah kaunsa hai?", "options": ["Earth", "Mercury", "Venus", "Mars"], "ans": 1},
        {"id": "s5", "q": "Bijli ka aavishkar kisne kiya?", "options": ["Newton", "Benjamin Franklin", "Nikola Tesla", "Einstein"], "ans": 1},
        {"id": "s6", "q": "Duniya ka sabse bada planet kaunsa hai?", "options": ["Earth", "Jupiter", "Saturn", "Neptune"], "ans": 1},
        {"id": "s7", "q": "Vayu mein oxygen kitna pratishat hai?", "options": ["21%", "50%", "10%", "78%"], "ans": 0},
        {"id": "s8", "q": "Light ki speed kitni hai?", "options": ["3 Lakh km/s", "1 Lakh km/s", "5 Lakh km/s", "10 Lakh km/s"], "ans": 0},
        {"id": "s9", "q": "Duniya ka sabse chhota jeev kaunsa hai?", "options": ["Virus", "Bacteria", "Amoeba", "Fungi"], "ans": 0},
        {"id": "s10", "q": "Khoon ka rang laal kyun hota hai?", "options": ["Iron", "Calcium", "Sodium", "Potassium"], "ans": 0}
    ],
    "History": [
        {"id": "h1", "q": "Bharat ko azaadi kab mili?", "options": ["1945", "1947", "1950", "1942"], "ans": 1},
        {"id": "h2", "q": "Taj Mahal kisne banwaya?", "options": ["Akbar", "Shah Jahan", "Babur", "Humayun"], "ans": 1},
        {"id": "h3", "q": "Bharat ka pehla Pradhan Mantri kaun tha?", "options": ["Nehru", "Patel", "Gandhi", "Ambedkar"], "ans": 0},
        {"id": "h4", "q": "Jhansi ki Rani ka naam kya tha?", "options": ["Lakshmi Bai", "Rani Padmavati", "Razia Sultan", "Rani Ahilya"], "ans": 0},
        {"id": "h5", "q": "Mahabharat kisne likhi thi?", "options": ["Valmiki", "Ved Vyas", "Tulsidas", "Kalidas"], "ans": 1},
        {"id": "h6", "q": "Dandi March kab hua tha?", "options": ["1930", "1942", "1920", "1919"], "ans": 0},
        {"id": "h7", "q": "Mughal samrajya ka sansthapak kaun tha?", "options": ["Akbar", "Babur", "Humayun", "Shah Jahan"], "ans": 1},
        {"id": "h8", "q": "Ashoka ne kis dharm ko apnaya?", "options": ["Hindu", "Buddhism", "Jain", "Sikh"], "ans": 1},
        {"id": "h9", "q": "Kalinga Yudh kisne jeeta tha?", "options": ["Ashoka", "Chandragupta", "Samudragupta", "Harsha"], "ans": 0},
        {"id": "h10", "q": "Bharat ka pehla rashtrapati kaun tha?", "options": ["Rajendra Prasad", "Nehru", "Radhakrishnan", "Zakir Hussain"], "ans": 0}
    ]
}
ALL_QUESTIONS["Mix (All)"] = ALL_QUESTIONS["Computer"] + ALL_QUESTIONS["General Knowledge"] + ALL_QUESTIONS["Science"] + ALL_QUESTIONS["History"]

# --- FRONTEND (HTML + JS + CSS) ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>KBC Ultimate Pro Max</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;600&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Teko', sans-serif; user-select: none; }
    body { background: #02040a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; background: radial-gradient(circle, #0a1128 0%, #000 100%); }
    
    .game-container {
      position: relative; width: 100%; max-width: 900px; height: 100vh; max-height: 850px;
      display: flex; background: rgba(5, 10, 31, 0.9); border: 2px solid #f1c40f; border-radius: 15px; overflow: hidden;
      box-shadow: 0 0 50px rgba(241, 196, 15, 0.3);
    }
    
    /* Main Area */
    .main-area { flex: 1; position: relative; display: flex; flex-direction: column; padding: 20px; }
    
    .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .quit-btn { background: #e74c3c; color: white; border: none; padding: 8px 20px; border-radius: 20px; font-size: 18px; cursor: pointer; font-weight: bold; box-shadow: 0 0 10px #e74c3c; }
    .timer-circle {
      width: 65px; height: 65px; border-radius: 50%; display: flex; justify-content: center; align-items: center;
      font-size: 32px; font-weight: bold; color: #f1c40f; border: 3px solid #f1c40f;
      box-shadow: 0 0 15px rgba(241, 196, 15, 0.8), inset 0 0 10px rgba(241,196,15,0.5);
      animation: pulse 2s infinite alternate;
    }
    @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.05); } }
    
    /* Lifelines */
    .lifelines { display: flex; gap: 15px; margin-bottom: 20px; }
    .lifeline-btn {
      width: 60px; height: 60px; border-radius: 50%; border: 2px solid #3498db;
      background: rgba(52, 152, 219, 0.2); color: #3498db; font-size: 20px; font-weight: bold;
      cursor: pointer; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: 0.3s;
      box-shadow: 0 0 15px rgba(52, 152, 219, 0.3);
    }
    .lifeline-btn span { font-size: 14px; color: #f1c40f; }
    .lifeline-btn:hover { background: rgba(52, 152, 219, 0.6); transform: scale(1.1); box-shadow: 0 0 25px #3498db; }
    .lifeline-btn:disabled { border-color: #444; color: #444; pointer-events: none; opacity: 0.3; box-shadow: none; }

    /* Quiz Area */
    .quiz-area { flex: 1; display: flex; flex-direction: column; justify-content: center; }
    .question-box {
      background: linear-gradient(90deg, rgba(0,0,0,0.8), rgba(26, 42, 108, 0.8), rgba(0,0,0,0.8));
      border: 2px solid #f1c40f; border-radius: 50px; padding: 25px;
      text-align: center; font-size: 26px; line-height: 1.3; margin-bottom: 30px;
      box-shadow: 0 0 30px rgba(241, 196, 15, 0.3);
    }
    .options { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .option {
      background: linear-gradient(90deg, #111, #1a1a1a); border: 2px solid #444;
      border-radius: 40px; padding: 15px 20px; font-size: 20px; cursor: pointer;
      display: flex; align-items: center; transition: 0.2s;
    }
    .option:hover { border-color: #f1c40f; background: #222; box-shadow: 0 0 15px #f1c40f; }
    .option span { color: #f1c40f; margin-right: 15px; font-weight: bold; font-size: 24px; }
    .option.correct { background: #2ecc71 !important; border-color: #fff; color: #000; box-shadow: 0 0 25px #2ecc71; }
    .option.wrong { background: #e74c3c !important; border-color: #fff; color: #fff; box-shadow: 0 0 25px #e74c3c; }
    .option.hidden { visibility: hidden; }

    /* Money Ladder */
    .money-ladder {
      width: 200px; background: rgba(0,0,0,0.7); border-left: 2px solid #f1c40f;
      padding: 10px; display: flex; flex-direction: column-reverse; justify-content: flex-start;
      overflow-y: auto; box-shadow: -5px 0 20px rgba(0,0,0,0.8);
    }
    .ladder-item {
      font-size: 18px; padding: 5px 10px; color: #888; display: flex; justify-content: space-between;
      border-radius: 5px; margin-bottom: 2px; transition: 0.3s;
    }
    .ladder-item.active { color: #000; font-weight: bold; background: #f1c40f; transform: scale(1.05); box-shadow: 0 0 10px #f1c40f;}
    .ladder-item.milestone { color: #2ecc71; font-weight: bold; }
    .ladder-item.milestone.active { color: #000; background: #2ecc71; box-shadow: 0 0 10px #2ecc71;}

    /* Overlays */
    .overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.95); display: flex; flex-direction: column; justify-content: center; align-items: center;
      z-index: 100; text-align: center; padding: 20px; backdrop-filter: blur(10px);
    }
    .overlay h2 { font-size: 50px; color: #f1c40f; margin-bottom: 10px; text-shadow: 0 0 20px #f1c40f; }
    .overlay p { font-size: 28px; margin-bottom: 30px; }
    .btn { padding: 15px 50px; font-size: 24px; background: #f1c40f; color: #000; border: none; border-radius: 30px; font-weight: bold; cursor: pointer; box-shadow: 0 0 20px rgba(241,196,15,0.6); margin: 10px; transition: 0.2s;}
    .btn:hover { transform: scale(1.05); }
    .btn-blue { background: #3498db; color: #fff; box-shadow: 0 0 20px rgba(52,152,219,0.6); }
    .btn-orange { background: #e67e22; color: #fff; box-shadow: 0 0 20px rgba(230,126,34,0.6); }
    .hidden { display: none !important; }

    .shop-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; width: 100%; max-width: 500px; }
    .shop-card { background: #111; border: 2px solid #444; border-radius: 10px; padding: 15px; text-align: center; }
    
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

  <div class="game-container">
    
    <!-- 1. Main Menu & Shop -->
    <div class="overlay" id="menuScreen">
      <h2>KBC Ultimate</h2>
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

    <!-- 2. Category Selection -->
    <div class="overlay hidden" id="categoryScreen">
      <h2>Select Category</h2>
      <div class="shop-grid" id="categoryGrid"></div>
    </div>

    <!-- 3. Main Game Area -->
    <div class="main-area hidden" id="mainGameArea">
      <div class="top-bar">
        <button class="quit-btn" id="quitBtn">Quit</button>
        <div class="timer-circle" id="timerDisplay">45</div>
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

    <!-- Money Ladder Sidebar -->
    <div class="money-ladder hidden" id="moneyLadder"></div>

    <!-- 4. Result Screen -->
    <div class="overlay hidden" id="resultScreen">
      <h2 id="resultTitle">Game Over</h2>
      <p>Tumne jeete: <span id="finalMoney" style="color:#2ecc71">₹ 0</span></p>
      <button class="btn" onclick="goHome()">Back to Home</button>
    </div>

  </div>

  <script>
    // --- AUDIO ENGINE ---
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

    // --- DATA ---
    const user = "player1";
    let userData = {};
    let gameQuestions = [];
    let currentQ = 0;
    let timeLeft = 45, timerInterval, canClick = false;
    
    const prizeMoney = ["₹ 1,000", "₹ 5,000", "₹ 10,000", "₹ 50,000", "₹ 1,00,000", "₹ 5,00,000", "₹ 10,00,000", "₹ 50,00,000", "₹ 1 CRORE"];

    // --- 1. FETCH DATA & INIT ---
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
        if ([3, 6, 8].includes(index)) div.classList.add("milestone");
        div.innerHTML = `<span>${index + 1}</span> <span>${amount}</span>`;
        div.id = `ladder-${index}`;
        ladder.appendChild(div);
      });
    }

    // --- 2. ADS & SHOP ---
    function watchAd() {
      let videoLink = "https://youtu.be/cLvpmdVrvag?si=bVI4pLZ6jRXO0qTX";
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

    // --- 3. GAME FLOW & 80/20 ALGORITHM ---
    function showCategories() {
      document.getElementById("menuScreen").classList.add("hidden");
      document.getElementById("categoryScreen").classList.remove("hidden");
      const grid = document.getElementById("categoryGrid");
      grid.innerHTML = "";
      const cats = ["Computer", "General Knowledge", "Science", "History", "Mix (All)"];
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
        }
      });
    }

    function loadQuestion() {
      if (currentQ >= gameQuestions.length) { endGame("win"); return; }
      
      canClick = true; timeLeft = 45;
      document.getElementById("timerDisplay").innerText = timeLeft;
      document.getElementById("timerDisplay").style.color = "#f1c40f";
      
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
        if (timeLeft <= 0) { clearInterval(timerInterval); endGame("timeout"); }
      }, 1000);
    }

    function checkAnswer(selected, el) {
      if (!canClick) return;
      canClick = false; clearInterval(timerInterval);
      
      let q = gameQuestions[currentQ];
      if (selected === q.ans) {
        el.classList.add("correct"); sounds.correct();
        setTimeout(() => { currentQ++; loadQuestion(); }, 1500);
      } else {
        el.classList.add("wrong"); sounds.wrong();
        setTimeout(() => document.getElementById("opt-" + q.ans).classList.add("correct"), 500);
        setTimeout(() => endGame("wrong"), 2000);
      }
    }

    // --- 4. LIFELINES ---
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
            alert(`Audience Poll:\\nOption ${q.ans} ko sabse zyada (60%) votes mile hain!`);
          } else if (type === 'phone') {
            alert(`Friend bolta hai: "Mujhe lagta hai sahi jawab Option ${q.ans} hai!"`);
          } else if (type === 'expert') {
            alert(`🧑‍🔬 Expert bolta hai: "100% guarantee ke sath, sahi jawab Option ${q.ans} hi hai."`);
          }
        }
      });
    }

    // --- 5. END GAME ---
    document.getElementById("quitBtn").onclick = () => { if (confirm("Quit karke paise lekar jao?")) endGame("quit"); };

    function endGame(reason) {
      canClick = false; clearInterval(timerInterval);
      document.getElementById("mainGameArea").classList.add("hidden");
      document.getElementById("moneyLadder").classList.add("hidden");
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
    
    seen_ids = users[username]["seen_questions"]
    category_pool = ALL_QUESTIONS.get(category, ALL_QUESTIONS["Mix (All)"])
    
    # --- 20% / 80% ALGORITHM ---
    new_pool = [q for q in category_pool if q["id"] not in seen_ids]
    old_pool = [q for q in category_pool if q["id"] in seen_ids]

    num_new_needed = int(9 * 0.8) 
    num_old_needed = 9 - num_new_needed 

    if len(new_pool) < num_new_needed:
        num_old_needed += (num_new_needed - len(new_pool))
        num_new_needed = len(new_pool)

    selected_new = random.sample(new_pool, num_new_needed) if new_pool else []
    selected_old = random.sample(old_pool, min(num_old_needed, len(old_pool))) if old_pool else []
    
    final_questions = selected_new + selected_old
    
    if len(final_questions) < 9:
        remaining = [q for q in category_pool if q not in final_questions]
        final_questions += random.sample(remaining, min(9 - len(final_questions), len(remaining)))

    random.shuffle(final_questions)

    for q in selected_new:
        if q["id"] not in users[username]["seen_questions"]:
            users[username]["seen_questions"].append(q["id"])

    if len(users[username]["seen_questions"]) > 50:
        users[username]["seen_questions"] = users[username]["seen_questions"][-50:]

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
