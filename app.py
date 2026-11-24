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

# --- DATABASE (Dynamic Users) ---
# Ab users khud register karenge. Demo ke liye ek test user:
users = {
    "admin": {"password": "123", "coins": 10000, "wallet": 0, "tickets": 0, "lifelines": {"5050": 1, "audience": 1, "phone": 1, "expert": 1}}
}

ipl_matches = {
    "match1": {
        "title": "MI vs CSK",
        "team_a": "Mumbai Indians",
        "team_b": "Chennai Super Kings",
        "pool_a": 0,
        "pool_b": 0,
        "status": "open",
        "winner": None
    }
}

user_bets = {}
active_game_answers = {}

# --- QUESTION BANK ---
REAL_QUESTIONS = [
    {"q": "Bharat ki rajdhani kya hai?", "correct": "New Delhi", "wrong": ["Mumbai", "Kolkata", "Chennai"]},
    {"q": "Sabse bada mahasagar kaunsa hai?", "correct": "Pacific Ocean", "wrong": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]},
    {"q": "Pani ka rasayanik sutra kya hai?", "correct": "H2O", "wrong": ["CO2", "O2", "NaCl"]},
    {"q": "HTML ka full form kya hai?", "correct": "Hyper Text Markup Language", "wrong": ["High Text Language", "Hyper Tabular", "Home Tool"]},
    {"q": "Bharat ko azaadi kab mili?", "correct": "1947", "wrong": ["1945", "1950", "1942"]},
]

def prepare_questions(category_pool):
    final_qs = []
    for idx, q_data in enumerate(category_pool):
        options = [q_data['correct']] + q_data['wrong']
        random.shuffle(options)
        ans_idx = options.index(q_data['correct'])
        final_qs.append({"id": f"q_{idx}", "q": q_data['q'], "options": options, "secure_ans": ans_idx})
    return final_qs

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>KBC Pro & IPL Prediction</title>
  <link rel="manifest" href="/manifest.json">
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
    
    .overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.95); display: flex; flex-direction: column; justify-content: center; align-items: center;
      z-index: 100; text-align: center; padding: 20px; backdrop-filter: blur(10px); overflow-y: auto;
    }
    .overlay h2 { font-size: 50px; color: #f1c40f; margin-bottom: 10px; text-shadow: 0 0 20px #f1c40f; }
    .overlay p { font-size: 24px; margin-bottom: 15px; }
    .btn { padding: 15px 40px; font-size: 22px; background: #f1c40f; color: #000; border: none; border-radius: 30px; font-weight: bold; cursor: pointer; box-shadow: 0 0 20px rgba(241,196,15,0.6); margin: 10px; transition: 0.2s;}
    .btn:hover { transform: scale(1.05); }
    .btn-blue { background: #3498db; color: #fff; box-shadow: 0 0 20px rgba(52,152,219,0.6); }
    .btn-orange { background: #e67e22; color: #fff; box-shadow: 0 0 20px rgba(230,126,34,0.6); }
    .btn-red { background: #e74c3c; color: #fff; box-shadow: 0 0 20px rgba(231,76,60,0.6); }
    .hidden { display: none !important; }

    .shop-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; width: 100%; max-width: 600px; }
    .shop-card { background: #111; border: 2px solid #444; border-radius: 10px; padding: 15px; text-align: center; display: flex; flex-direction: column; justify-content: space-between;}

    /* Forms */
    input[type="text"], input[type="password"], input[type="number"] { width: 100%; padding: 12px; font-size: 20px; border-radius: 10px; border: 2px solid #f1c40f; background: #000; color: white; margin-bottom: 15px; text-align: center; }

    .match-card {
        background: #111a3a; border: 2px solid #f1c40f; border-radius: 15px; padding: 15px; margin-bottom: 15px; width: 100%; max-width: 600px;
    }
    .match-teams { display: flex; justify-content: space-between; align-items: center; font-size: 24px; font-weight: bold; margin-bottom: 15px; }
    .team-box { flex: 1; text-align: center; padding: 10px; border: 1px solid #444; border-radius: 10px; cursor: pointer; transition: 0.2s; }
    .team-box:hover { background: rgba(241, 196, 15, 0.1); border-color: #f1c40f; }
    .vs { margin: 0 10px; color: #f1c40f; }
    
    .leaderboard-list { width: 100%; max-width: 500px; margin-top: 20px; }
    .leaderboard-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #333; font-size: 22px; }
    
    .wallet-box { background: #1a2a6c; border: 2px solid #2ecc71; border-radius: 15px; padding: 20px; margin-bottom: 20px; width: 100%; max-width: 400px;}
    
    @media (max-width: 700px) {
      .shop-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <div class="game-container" id="gameContainer">
    
    <!-- LOGIN / REGISTER SCREEN -->
    <div class="overlay" id="loginScreen">
      <h2>Login / Register</h2>
      <input type="text" id="loginUser" placeholder="Enter Username">
      <input type="password" id="loginPass" placeholder="Enter Password">
      
      <button class="btn btn-blue" onclick="loginUser()">Login</button>
      <button class="btn btn-orange" onclick="registerUser()">Register New</button>
    </div>

    <!-- Main Menu -->
    <div class="overlay hidden" id="menuScreen">
      <h2>KBC & IPL Pro</h2>
      <p>Welcome, <span id="userNameDisplay" style="color: #2ecc71; font-weight: bold;">User</span></p>
      
      <div style="font-size: 24px; margin-bottom: 10px; display: flex; justify-content: center; gap: 20px;">
        <span>🪙 Game Coins: <b id="coinBalance" style="color:#f1c40f">0</b></span>
        <span>💳 Wallet: <b id="walletBalance" style="color:#2ecc71">0</b></span>
      </div>
      
      <div class="shop-grid">
        <div class="shop-card">
          <h3 style="color: #e67e22; font-size: 22px;">Earn Coins</h3>
          <button class="btn btn-orange" style="padding: 10px; font-size: 18px;" onclick="showAd('coins')">Watch Ad (+100)</button>
        </div>
        <div class="shop-card">
          <h3 style="color: #f1c40f; font-size: 22px;">IPL Prediction</h3>
          <button class="btn" style="padding: 10px; font-size: 18px;" onclick="showIPL()">Play IPL</button>
        </div>
        <div class="shop-card" style="border-color: #2ecc71;">
          <h3 style="color: #2ecc71; font-size: 22px;">Withdraw Coins</h3>
          <button class="btn" style="padding: 10px; font-size: 18px; background: #2ecc71; color: black;" onclick="showWithdraw()">Withdraw Now</button>
        </div>
        <div class="shop-card" style="border-color: #9b59b6;">
          <h3 style="color: #9b59b6; font-size: 22px;">Leaderboard</h3>
          <button class="btn" style="padding: 10px; font-size: 18px; background: #9b59b6;" onclick="showLeaderboard()">View Top 10</button>
        </div>
      </div>
      <button class="btn btn-red" style="margin-top: 20px;" onclick="logout()">Logout</button>
    </div>

    <!-- Withdraw Screen -->
    <div class="overlay hidden" id="withdrawScreen">
      <h2>My Wallet</h2>
      <div class="wallet-box">
        <h3>Wallet Balance: <span id="walletAmt" style="color: #2ecc71;">0</span></h3>
      </div>
      <input type="number" id="withdrawAmount" placeholder="Enter Coins to Withdraw">
      <button class="btn btn-blue" onclick="processWithdraw()">Transfer to Wallet</button>
      <button class="btn btn-red" style="margin-top: 20px;" onclick="goHome()">Back</button>
    </div>

    <!-- IPL Screen -->
    <div class="overlay hidden" id="iplScreen">
      <h2>IPL Prediction</h2>
      <div id="matchesContainer" style="width: 100%; display: flex; flex-direction: column; align-items: center;"></div>

      <div id="betSection" class="hidden" style="margin-top: 20px; background: #111; padding: 20px; border-radius: 15px; border: 1px solid #f1c40f; width: 90%; max-width: 400px;">
          <h3 style="color: #f1c40f;">Place Your Bet</h3>
          <p id="selectedTeamText" style="font-size: 20px; color: white;"></p>
          <p id="currentOddsText" style="font-size: 18px; color: #2ecc71;"></p>
          <input type="number" id="betAmount" placeholder="Enter Coins" min="10">
          <p id="potentialPayout" style="color: #f1c40f; font-size: 18px; margin-bottom: 10px;"></p>
          <button class="btn btn-blue" onclick="placeBet()">Confirm Bet</button>
      </div>
      <button class="btn btn-red" style="margin-top: 20px;" onclick="goHome()">Back</button>
    </div>

    <!-- Leaderboard Screen -->
    <div class="overlay hidden" id="leaderboardScreen">
      <h2>Top Players</h2>
      <div class="leaderboard-list" id="leaderboardContainer"></div>
      <button class="btn btn-red" style="margin-top: 20px;" onclick="goHome()">Back</button>
    </div>

    <!-- Ad Overlay -->
    <div class="overlay" id="adOverlay" style="display: none; background: #000; z-index: 200;">
      <h2 style="color: #fff;">Advertisement</h2>
      <div id="adTimerLarge" style="font-size: 80px; color: #fff; margin: 20px 0; font-weight: bold;">15</div>
      <button class="btn btn-blue" id="claimAdBtn" style="display: none;" onclick="claimAdReward()">Claim Reward</button>
    </div>

  </div>

  <script>
    let currentUser = "";
    let userData = {};
    let adInterval;
    let matchesData = {};
    let selectedMatchId = null;
    let selectedTeam = null;
    let lockedOdds = 0.0;
    let iplLiveTimer;

    // Check if user is already logged in
    window.onload = () => {
        let savedUser = localStorage.getItem("kbc_logged_user");
        if(savedUser) {
            currentUser = savedUser;
            startGame();
        }
    }

    // --- AUTHENTICATION ---
    function registerUser() {
        let u = document.getElementById("loginUser").value;
        let p = document.getElementById("loginPass").value;
        if(!u || !p) { alert("Enter username and password"); return; }

        fetch('/api/register', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        }).then(res => res.json()).then(data => {
            if(data.status === "success") {
                alert("Registered successfully! Please login.");
            } else {
                alert(data.message);
            }
        });
    }

    function loginUser() {
        let u = document.getElementById("loginUser").value;
        let p = document.getElementById("loginPass").value;

        fetch('/api/login', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        }).then(res => res.json()).then(data => {
            if(data.status === "success") {
                currentUser = u;
                localStorage.setItem("kbc_logged_user", u);
                startGame();
            } else {
                alert("Invalid Credentials");
            }
        });
    }

    function logout() {
        localStorage.removeItem("kbc_logged_user");
        location.reload();
    }

    function startGame() {
        document.getElementById("loginScreen").classList.add("hidden");
        document.getElementById("menuScreen").classList.remove("hidden");
        document.getElementById("userNameDisplay").innerText = currentUser;
        fetchData();
    }

    function fetchData() {
      fetch('/api/get_data/' + currentUser).then(res => res.json()).then(data => {
          userData = data;
          document.getElementById("coinBalance").innerText = data.coins;
          document.getElementById("walletBalance").innerText = data.wallet;
          document.getElementById("walletAmt").innerText = data.wallet;
      });
    }

    // --- WITHDRAW LOGIC ---
    function showWithdraw() {
        document.getElementById("menuScreen").classList.add("hidden");
        document.getElementById("withdrawScreen").classList.remove("hidden");
    }

    function processWithdraw() {
        let amt = parseInt(document.getElementById("withdrawAmount").value);
        if(!amt || amt < 100) { alert("Minimum 100 Coins withdraw kar sakte hain."); return; }
        if(amt > userData.coins) { alert("Itne coins nahi hain!"); return; }

        fetch('/api/withdraw', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser, amount: amt})
        }).then(res => res.json()).then(data => {
            if(data.status === "success") {
                alert("Coins Wallet mein transfer ho gaye!");
                fetchData();
            }
        });
    }

    // --- IPL LOGIC ---
    function showIPL() {
        document.getElementById("menuScreen").classList.add("hidden");
        document.getElementById("iplScreen").classList.remove("hidden");
        loadMatches(); 
        clearInterval(iplLiveTimer);
        iplLiveTimer = setInterval(() => { loadMatches(); }, 5000); 
    }

    function loadMatches() {
        fetch('/api/ipl/get_matches').then(res => res.json()).then(data => {
            matchesData = data.matches;
            let container = document.getElementById("matchesContainer");
            container.innerHTML = "";
            
            for (let mId in matchesData) {
                let match = matchesData[mId];
                if (match.status !== "open") continue;

                let totalPool = match.pool_a + match.pool_b;
                let odds_a = "1.00", odds_b = "1.00";
                if (totalPool > 0) {
                    if (match.pool_a > 0) odds_a = ((totalPool * 0.98) / match.pool_a).toFixed(2);
                    if (match.pool_b > 0) odds_b = ((totalPool * 0.98) / match.pool_b).toFixed(2);
                }

                let card = document.createElement("div");
                card.className = "match-card";
                card.innerHTML = `
                    <div class="match-teams">
                        <div class="team-box" onclick="selectTeam('${mId}', 'team_a', ${odds_a})">
                            <div>${match.team_a}</div>
                            <div style="font-size: 14px; color: #aaa;">Pool: ${match.pool_a}</div>
                            <div style="font-size: 16px; color: #2ecc71;">Odds: x${odds_a}</div>
                        </div>
                        <div class="vs">VS</div>
                        <div class="team-box" onclick="selectTeam('${mId}', 'team_b', ${odds_b})">
                            <div>${match.team_b}</div>
                            <div style="font-size: 14px; color: #aaa;">Pool: ${match.pool_b}</div>
                            <div style="font-size: 16px; color: #2ecc71;">Odds: x${odds_b}</div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            }
        });
    }

    function selectTeam(matchId, team, odds) {
        selectedMatchId = matchId;
        selectedTeam = team;
        lockedOdds = parseFloat(odds);
        document.getElementById("betSection").classList.remove("hidden");
        document.getElementById("selectedTeamText").innerText = "Selected: " + matchesData[matchId][team];
        document.getElementById("currentOddsText").innerText = "Current Locked Rate: x" + lockedOdds;
        document.getElementById("betAmount").value = "";
        document.getElementById("potentialPayout").innerText = "Potential Return: 0 Coins";
    }

    function updatePotential() {
        let amt = parseInt(document.getElementById("betAmount").value) || 0;
        let payout = Math.floor(amt * lockedOdds);
        document.getElementById("potentialPayout").innerText = "Potential Return: " + payout + " Coins";
    }

    document.getElementById("betAmount")?.addEventListener('input', updatePotential);

    function placeBet() {
        let amount = parseInt(document.getElementById("betAmount").value);
        if (!amount || amount < 10) { alert("Minimum 10 coins lagayein."); return; }
        if (amount > userData.coins) { alert("Aapke paas itne coins nahi hain!"); return; }

        fetch('/api/ipl/place_bet', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser, match_id: selectedMatchId, team: selectedTeam, amount: amount, odds: lockedOdds})
        }).then(res => res.json()).then(data => {
            if(data.status === "success") {
                alert("Bet lag gayi! Rate lock ho gaya: x" + lockedOdds);
                fetchData();
                loadMatches();
                document.getElementById("betSection").classList.add("hidden");
            } else {
                alert("Error: " + data.message);
            }
        });
    }

    // --- LEADERBOARD ---
    function showLeaderboard() {
        document.getElementById("menuScreen").classList.add("hidden");
        document.getElementById("leaderboardScreen").classList.remove("hidden");
        fetch('/api/leaderboard').then(res => res.json()).then(data => {
            let container = document.getElementById("leaderboardContainer");
            container.innerHTML = "";
            data.top_users.forEach((u, index) => {
                let div = document.createElement("div");
                div.className = "leaderboard-item";
                div.innerHTML = `<span>#${index+1} ${u.name}</span> <span>🪙 ${u.coins}</span>`;
                container.appendChild(div);
            });
        });
    }

    function goHome() {
        clearInterval(iplLiveTimer); 
        document.getElementById("withdrawScreen").classList.add("hidden");
        document.getElementById("leaderboardScreen").classList.add("hidden");
        document.getElementById("iplScreen").classList.add("hidden");
        document.getElementById("menuScreen").classList.remove("hidden");
        fetchData();
    }

    // Ad Logic
    function showAd(action) {
      window.open("https://asiafilm.org/4/23852721a9ede5c4d23ead1ed92dadc3", '_blank');
      document.getElementById("adOverlay").style.display = "flex";
      document.getElementById("claimAdBtn").style.display = "none";
      let waitTime = 15;
      document.getElementById("adTimerLarge").innerText = waitTime;
      clearInterval(adInterval);
      adInterval = setInterval(() => {
        waitTime--;
        document.getElementById("adTimerLarge").innerText = waitTime;
        if (waitTime <= 0) {
          clearInterval(adInterval);
          document.getElementById("claimAdBtn").style.display = "block";
        }
      }, 1000);
    }

    function claimAdReward() {
      document.getElementById("adOverlay").style.display = "none";
      fetch('/api/ad_reward_coins', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: currentUser}) })
      .then(res => res.json()).then(data => fetchData());
    }
  </script>
</body>
</html>
"""

# --- BACKEND API ROUTES ---
@app.route('/')
def home(): return render_template_string(HTML_CODE)

@app.route('/manifest.json')
def manifest():
    return jsonify({"name": "KBC & IPL", "short_name": "KBC", "start_url": "/", "display": "standalone", "background_color": "#02040a", "theme_color": "#f1c40f", "icons": [{"src": "https://raw.githubusercontent.com/ayannuman800-del/kbc-game/main/1794342592618.png", "sizes": "512x512", "type": "image/png"}]})

# --- AUTH APIS ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"})
    if username in users:
        return jsonify({"status": "error", "message": "Username already taken"})
    
    users[username] = {
        "password": password, 
        "coins": 500, # Naye user ko 500 free coins
        "wallet": 0, 
        "tickets": 0, 
        "lifelines": {"5050": 1, "audience": 1, "phone": 1, "expert": 1}
    }
    return jsonify({"status": "success", "message": "Registered successfully"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username]['password'] == password:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"})

# --- USER APIS ---
@app.route('/api/get_data/<username>', methods=['GET'])
def get_data(username):
    if username in users:
        # Password ko frontend pe mat bhejo
        safe_data = {k: v for k, v in users[username].items() if k != 'password'}
        return jsonify(safe_data)
    return jsonify({"status": "error"})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    sorted_users = sorted(users.items(), key=lambda x: x[1]['coins'], reverse=True)[:10]
    top_users = [{"name": k, "coins": v['coins']} for k, v in sorted_users]
    return jsonify({"top_users": top_users})

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    username = data.get('username')
    amount = data.get('amount')

    if username in users and users[username]['coins'] >= amount:
        users[username]['coins'] -= amount
        users[username]['wallet'] += amount 
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Not enough coins"})

# --- IPL APIS ---
@app.route('/api/ipl/get_matches', methods=['GET'])
def get_matches():
    return jsonify({"matches": ipl_matches})

@app.route('/api/ipl/place_bet', methods=['POST'])
def place_bet():
    data = request.json
    username = data.get('username')
    match_id = data.get('match_id')
    team = data.get('team')
    amount = data.get('amount')
    locked_odds = data.get('odds') 

    if username not in users: return jsonify({"status": "error", "message": "User not found"})
    if users[username]['coins'] < amount: return jsonify({"status": "error", "message": "Not enough coins"})
    if match_id not in ipl_matches or ipl_matches[match_id]['status'] != 'open': return jsonify({"status": "error", "message": "Match closed"})

    users[username]['coins'] -= amount
    
    if team == 'team_a': ipl_matches[match_id]['pool_a'] += amount
    else: ipl_matches[match_id]['pool_b'] += amount

    if username not in user_bets: user_bets[username] = []
    
    user_bets[username].append({
        "match_id": match_id, 
        "team": team, 
        "amount": amount,
        "locked_odds": locked_odds,
        "potential_payout": int(amount * locked_odds)
    })

    return jsonify({"status": "success"})

@app.route('/api/ipl/admin_resolve', methods=['POST'])
def admin_resolve():
    data = request.json
    match_id = data.get('match_id')
    winner = data.get('winner')
    admin_pass = data.get('password')

    if admin_pass != "moayan_admin":
        return jsonify({"status": "error", "message": "Unauthorized"})

    if match_id not in ipl_matches: return jsonify({"status": "error"})
    
    match = ipl_matches[match_id]
    if match['status'] != 'open': return jsonify({"status": "error", "message": "Already resolved"})

    match['status'] = 'finished'
    match['winner'] = winner

    for username, bets in user_bets.items():
        for bet in bets:
            if bet['match_id'] == match_id and bet['team'] == winner:
                payout = bet['potential_payout']
                users[username]['coins'] += payout

    return jsonify({"status": "success", "message": "Odds Locked Payouts Distributed!"})

@app.route('/api/ad_reward_coins', methods=['POST'])
def ad_reward_coins():
    username = request.json.get('username')
    if username in users:
        users[username]["coins"] += 100
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
