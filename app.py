from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# --- VIRTUAL DATABASE (Refresh hone par bhi safe rahega) ---
# Abhi ke liye hum memory use kar rahe hain, real app mein MongoDB use hoga.
users = {
    "player1": {"balance": 100000, "positions": [], "history": []}
}

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paper Trading - Pro</title>
    <!-- TradingView Lightweight Charts Library -->
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #131722; color: #d1d4dc; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        
        /* Header */
        #header { background: #1e222d; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2e39; }
        #header h1 { font-size: 20px; color: #fff; margin-right: 20px;}
        .stats { display: flex; gap: 20px; font-size: 16px; }
        .stats span { color: #2ecc71; font-weight: bold; }
        
        /* Main Layout */
        #main { display: flex; flex: 1; overflow: hidden; }
        #chart-container { flex: 1; position: relative; }
        
        /* Side Panel */
        #panel { width: 320px; background: #1e222d; border-left: 1px solid #2a2e39; display: flex; flex-direction: column; overflow-y: auto;}
        .section { padding: 15px; border-bottom: 1px solid #2a2e39; }
        .section h3 { font-size: 16px; color: #f1c40f; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Inputs & Buttons */
        input[type="number"], input[type="text"] { width: 100%; padding: 10px; margin-bottom: 10px; background: #131722; border: 1px solid #2a2e39; color: white; border-radius: 5px; outline: none; }
        input:focus { border-color: #3498db; }
        
        .btn-group { display: flex; gap: 10px; }
        .btn { flex: 1; padding: 12px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; color: white; transition: 0.2s; }
        .btn-buy { background: #089981; }
        .btn-buy:hover { background: #067a67; }
        .btn-sell { background: #f23645; }
        .btn-sell:hover { background: #c02935; }
        .btn-close { background: #e67e22; padding: 5px 10px; font-size: 12px; width: auto;}

        /* Tables */
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; color: #888; padding-bottom: 5px; border-bottom: 1px solid #333; }
        td { padding: 8px 0; border-bottom: 1px solid #222; }
        .green { color: #089981; }
        .red { color: #f23645; }
        
        /* Top Toolbar (Timeframes) */
        #toolbar { position: absolute; top: 10px; left: 10px; z-index: 10; display: flex; gap: 5px; background: rgba(30,34,45,0.8); padding: 5px; border-radius: 5px; }
        .tf-btn { background: transparent; border: none; color: #d1d4dc; cursor: pointer; padding: 5px 10px; border-radius: 3px; }
        .tf-btn.active { background: #3498db; color: white; }
        
        /* Replay Controls */
        #replay-controls { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); display: none; gap: 10px; background: #1e222d; padding: 10px; border-radius: 8px; border: 1px solid #f1c40f; z-index: 10; }
        .replay-btn { background: #f1c40f; color: black; border: none; padding: 8px 15px; border-radius: 5px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>

    <div id="header">
        <div style="display:flex; align-items:center;">
            <h1>BTC/USDT</h1>
            <button class="btn" style="background:#3498db; padding: 5px 10px; flex:none; margin-left:10px;" onclick="toggleReplay()">Replay Mode</button>
        </div>
        <div class="stats">
            <div>Wallet: $<span id="wallet-balance">100000</span></div>
            <div>Live P&L: $<span id="live-pnl">0.00</span></div>
        </div>
    </div>

    <div id="main">
        <div id="chart-container">
            <div id="toolbar">
                <button class="tf-btn active" onclick="changeTF('1m', this)">1m</button>
                <button class="tf-btn" onclick="changeTF('5m', this)">5m</button>
                <button class="tf-btn" onclick="changeTF('15m', this)">15m</button>
                <button class="tf-btn" onclick="changeTF('1h', this)">1h</button>
            </div>
            <div id="replay-controls">
                <button class="replay-btn" onclick="playReplay()">▶ Play</button>
                <button class="replay-btn" onclick="stopReplay()">⏹ Stop</button>
            </div>
        </div>

        <div id="panel">
            <!-- Trade Section -->
            <div class="section">
                <h3>Place Order</h3>
                <input type="number" id="qty" placeholder="Quantity (e.g., 0.01)" step="0.001" value="0.1">
                <input type="text" id="note" placeholder="Why are you taking this trade?">
                <div class="btn-group">
                    <button class="btn btn-buy" onclick="placeOrder('BUY')">BUY / LONG</button>
                    <button class="btn btn-sell" onclick="placeOrder('SELL')">SELL / SHORT</button>
                </div>
            </div>

            <!-- Open Positions -->
            <div class="section">
                <h3>Open Positions</h3>
                <table id="open-table">
                    <thead>
                        <tr><th>Type</th><th>Qty</th><th>Entry</th><th>P&L</th><th>Action</th></tr>
                    </thead>
                    <tbody id="open-body"></tbody>
                </table>
                <p id="no-pos" style="text-align:center; color:#666; font-size:12px; margin-top:10px;">No open positions</p>
            </div>

            <!-- Trade History -->
            <div class="section">
                <h3>Trade History & Notes</h3>
                <table id="history-table">
                    <thead>
                        <tr><th>Type</th><th>Price</th><th>P&L</th><th>Note</th></tr>
                    </thead>
                    <tbody id="history-body"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let chart, candleSeries, currentPrice = 0;
        let currentTF = '1m';
        let isReplay = false, replayData = [], replayIndex = 0, replayInterval;

        // 1. Initialize Chart
        const chartContainer = document.getElementById('chart-container');
        chart = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight,
            layout: { backgroundColor: '#131722', textColor: '#d1d4dc' },
            grid: { vertLines: { color: '#2a2e39' }, horzLines: { color: '#2a2e39' } },
            crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
            timeScale: { timeVisible: true, secondsVisible: false },
        });

        candleSeries = chart.addCandlestickSeries({
            upColor: '#089981', downColor: '#f23645', borderVisible: false,
            wickUpColor: '#089981', wickDownColor: '#f23645',
        });

        window.addEventListener('resize', () => {
            chart.applyOptions({ width: chartContainer.clientWidth, height: chartContainer.clientHeight });
        });

        // 2. Fetch Data
        async function fetchKlines(tf) {
            try {
                // Backend proxy se data fetch kar rahe hain CORS error se bachne ke liye
                let res = await fetch(`/api/klines?interval=${tf}&limit=200`);
                let data = await res.json();
                let formattedData = data.map(d => ({
                    time: d[0] / 1000, open: parseFloat(d[1]), high: parseFloat(d[2]), low: parseFloat(d[3]), close: parseFloat(d[4])
                }));
                candleSeries.setData(formattedData);
                currentPrice = formattedData[formattedData.length - 1].close;
                updatePositionsUI(); // Update P&L after new data
            } catch(e) { console.error("Chart Data Error", e); }
        }

        // 3. Live Price Polling (Every 2 seconds)
        setInterval(async () => {
            if(isReplay) return; // Don't poll if replaying
            try {
                let res = await fetch(`/api/live_price`);
                let data = await res.json();
                currentPrice = data.price;
                
                // Update the last candle
                candleSeries.update({
                    time: Math.floor(Date.now() / 1000),
                    open: currentPrice, high: currentPrice, low: currentPrice, close: currentPrice
                });
                
                calculatePnL();
            } catch(e) { }
        }, 2000);

        // 4. Change Timeframe
        function changeTF(tf, btn) {
            document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTF = tf;
            fetchKlines(tf);
        }

        // 5. Trading Logic
        async function placeOrder(type) {
            let qty = parseFloat(document.getElementById('qty').value);
            let note = document.getElementById('note').value;
            if(!qty || qty <= 0) { alert("Enter valid quantity"); return; }
            if(!note) { alert("Please write your reasoning (Note) before trading!"); return; }

            let res = await fetch('/api/trade', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ type: type, qty: qty, price: currentPrice, note: note })
            });
            let data = await res.json();
            
            if(data.status === "success") {
                document.getElementById('note').value = ""; // clear note
                document.getElementById('wallet-balance').innerText = data.balance.toFixed(2);
                updatePositionsUI(data.positions);
            } else {
                alert(data.message);
            }
        }

        function closePosition(index) {
            fetch('/api/close', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ index: index, close_price: currentPrice })
            }).then(res => res.json()).then(data => {
                if(data.status === "success") {
                    document.getElementById('wallet-balance').innerText = data.balance.toFixed(2);
                    updatePositionsUI(data.positions, data.history);
                }
            });
        }

        // 6. UI Updates & P&L
        let myPositions = [];
        function updatePositionsUI(positions = null, history = null) {
            if(positions) myPositions = positions;
            let tbody = document.getElementById('open-body');
            tbody.innerHTML = "";
            
            if(myPositions.length === 0) {
                document.getElementById('no-pos').style.display = 'block';
            } else {
                document.getElementById('no-pos').style.display = 'none';
                myPositions.forEach((p, i) => {
                    let tr = document.createElement('tr');
                    tr.innerHTML = `<td class="${p.type === 'BUY' ? 'green' : 'red'}">${p.type}</td>
                                    <td>${p.qty}</td><td>${p.entry.toFixed(2)}</td>
                                    <td id="pnl-${i}">0.00</td>
                                    <td><button class="btn btn-close" onclick="closePosition(${i})">Close</button></td>`;
                    tbody.appendChild(tr);
                });
            }
            
            if(history) {
                let htbody = document.getElementById('history-body');
                htbody.innerHTML = "";
                history.slice().reverse().forEach(h => {
                    let tr = document.createElement('tr');
                    tr.innerHTML = `<td class="${h.type === 'BUY' ? 'green' : 'red'}">${h.type}</td>
                                    <td>${h.close_price.toFixed(2)}</td>
                                    <td class="${h.pnl >= 0 ? 'green' : 'red'}">${h.pnl.toFixed(2)}</td>
                                    <td style="font-size:10px; color:#888;">${h.note}</td>`;
                    htbody.appendChild(tr);
                });
            }
            calculatePnL();
        }

        function calculatePnL() {
            let totalPnl = 0;
            myPositions.forEach((p, i) => {
                let pnl = p.type === 'BUY' ? (currentPrice - p.entry) * p.qty : (p.entry - currentPrice) * p.qty;
                totalPnl += pnl;
                let el = document.getElementById(`pnl-${i}`);
                if(el) { el.innerText = pnl.toFixed(2); el.className = pnl >= 0 ? 'green' : 'red'; }
            });
            let pnlEl = document.getElementById('live-pnl');
            pnlEl.innerText = totalPnl.toFixed(2);
            pnlEl.className = totalPnl >= 0 ? 'green' : 'red';
        }

        // 7. Replay Logic (Simple Implementation)
        async function toggleReplay() {
            if(isReplay) { stopReplay(); return; }
            isReplay = true;
            document.getElementById('replay-controls').style.display = 'flex';
            // Fetch 300 candles
            let res = await fetch(`/api/klines?interval=${currentTF}&limit=300`);
            let data = await res.json();
            
            // Format all
            let allCandles = data.map(d => ({
                time: d[0] / 1000, open: parseFloat(d[1]), high: parseFloat(d[2]), low: parseFloat(d[3]), close: parseFloat(d[4])
            }));
            
            // Hide the last 100 for replay
            replayData = allCandles.slice(-100);
            let initialData = allCandles.slice(0, 200);
            candleSeries.setData(initialData);
            replayIndex = 0;
        }

        function playReplay() {
            if(replayInterval) clearInterval(replayInterval);
            replayInterval = setInterval(() => {
                if(replayIndex >= replayData.length) { clearInterval(replayInterval); return; }
                candleSeries.update(replayData[replayIndex]);
                currentPrice = replayData[replayIndex].close;
                replayIndex++;
                calculatePnL();
            }, 1000); // 1 sec per candle
        }

        function stopReplay() {
            isReplay = false;
            clearInterval(replayInterval);
            document.getElementById('replay-controls').style.display = 'none';
            fetchKlines(currentTF);
        }

        // Init
        fetchKlines('1m');
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_CODE)

# --- BINANCE API PROXY ---
@app.route('/api/klines')
def get_klines():
    try:
        tf = request.args.get('interval', '1m')
        limit = request.args.get('limit', 200)
        url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={tf}&limit={limit}"
        res = requests.get(url)
        return jsonify(res.json())
    except:
        return jsonify([])

@app.route('/api/live_price')
def live_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url)
        return jsonify({"price": float(res.json()['price'])})
    except:
        return jsonify({"price": 0})

# --- TRADING LOGIC ---
@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json
    user = users["player1"]
    
    user['positions'].append({
        "type": data['type'],
        "qty": data['qty'],
        "entry": data['price'],
        "note": data['note']
    })
    return jsonify({"status": "success", "balance": user['balance'], "positions": user['positions']})

@app.route('/api/close', methods=['POST'])
def close_trade():
    data = request.json
    user = users["player1"]
    index = data['index']
    close_price = data['close_price']
    
    if 0 <= index < len(user['positions']):
        pos = user['positions'].pop(index)
        pnl = (close_price - pos['entry']) * pos['qty'] if pos['type'] == 'BUY' else (pos['entry'] - close_price) * pos['qty']
        
        user['balance'] += pnl
        user['history'].append({
            "type": pos['type'],
            "qty": pos['qty'],
            "entry": pos['entry'],
            "close_price": close_price,
            "pnl": pnl,
            "note": pos['note']
        })
        
    return jsonify({"status": "success", "balance": user['balance'], "positions": user['positions'], "history": user['history']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
