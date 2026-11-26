from flask import Flask, render_template_string

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Groww Pro | Ultimate Paper Trading</title>
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        :root {
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --bg-hover: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --green: #10b981;
            --red: #ef4444;
            --primary: #3b82f6;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-main); color: var(--text-main); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        
        /* HEADER */
        .header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); z-index: 100; }
        .logo { font-size: 20px; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 8px; }
        .tag { font-size: 10px; background: var(--primary); color: white; padding: 2px 6px; border-radius: 4px; }
        
        .wallet-info { display: flex; gap: 20px; }
        .w-item { display: flex; flex-direction: column; align-items: flex-end; }
        .w-item .lbl { font-size: 11px; color: var(--text-muted); }
        .w-item .val { font-size: 16px; font-weight: 600; }
        .text-green { color: var(--green) !important; }
        .text-red { color: var(--red) !important; }

        /* MAIN LAYOUT */
        .main-container { display: flex; flex: 1; overflow: hidden; }
        
        /* TABS */
        .tabs { display: flex; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); }
        .tab { flex: 1; text-align: center; padding: 12px; cursor: pointer; font-size: 14px; font-weight: 500; color: var(--text-muted); border-bottom: 2px solid transparent; }
        .tab.active { color: var(--primary); border-bottom: 2px solid var(--primary); background: rgba(59, 130, 246, 0.1); }
        
        .content-area { flex: 1; display: flex; flex-direction: column; position: relative; overflow: hidden; }

        /* DASHBOARD */
        #dashboard-view { padding: 15px; overflow-y: auto; height: 100%; }
        .indices { display: flex; gap: 15px; margin-bottom: 20px; }
        .index-card { flex: 1; background: var(--bg-card); border: 1px solid var(--bg-hover); border-radius: 12px; padding: 15px; cursor: pointer; }
        .index-card:hover { border-color: var(--primary); }
        .index-card h4 { font-size: 14px; color: var(--text-muted); margin-bottom: 8px; }
        .index-card h2 { font-size: 22px; font-weight: 700; }
        
        .stock-list { display: flex; flex-direction: column; gap: 10px; }
        .stock-item { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); padding: 15px; border-radius: 10px; border: 1px solid var(--bg-hover); cursor: pointer; }
        .stock-item:hover { background: var(--bg-hover); }
        .stock-details h3 { font-size: 15px; }
        .stock-price h3 { font-size: 15px; }

        /* CHART VIEW */
        #chart-view { display: none; flex-direction: column; height: 100%; background: var(--bg-main); }
        .chart-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); }
        .back-btn { background: none; border: none; color: var(--text-main); font-size: 20px; cursor: pointer; }
        
        .toolbar { display: flex; gap: 10px; padding: 10px 15px; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); }
        .btn-group { display: flex; gap: 5px; }
        .btn { padding: 6px 12px; border: 1px solid var(--bg-hover); background: var(--bg-main); color: var(--text-muted); border-radius: 6px; cursor: pointer; font-size: 12px; }
        .btn.active { background: var(--primary); color: white; border-color: var(--primary); }
        
        /* PURE CANVAS CHART */
        .canvas-container { flex: 1; position: relative; width: 100%; min-height: 350px; background: #0f172a; }
        #tradeCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }

        /* TRADE PANEL */
        .trade-panel { width: 320px; background: var(--bg-card); border-left: 1px solid var(--bg-hover); display: flex; flex-direction: column; overflow-y: auto; }
        .panel-section { padding: 15px; border-bottom: 1px solid var(--bg-hover); }
        .panel-title { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; text-transform: uppercase; }
        
        .input-group { margin-bottom: 12px; }
        .input-group label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
        .input-group input { width: 100%; padding: 10px; background: var(--bg-main); border: 1px solid var(--bg-hover); color: var(--text-main); border-radius: 8px; }
        
        .action-btns { display: flex; gap: 10px; }
        .btn-action { flex: 1; padding: 12px; border: none; border-radius: 8px; font-weight: 700; font-size: 15px; color: white; cursor: pointer; }
        .btn-buy { background: var(--green); }
        .btn-sell { background: var(--red); }

        /* POSITIONS */
        .pos-card { background: var(--bg-main); border: 1px solid var(--bg-hover); padding: 12px; border-radius: 8px; margin-bottom: 10px; }
        .pos-header { display: flex; justify-content: space-between; font-weight: 600; font-size: 14px; }
        .btn-close { width: 100%; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--red); color: var(--red); padding: 8px; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer; margin-top: 8px;}

        /* MODAL */
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: var(--bg-card); width: 90%; max-width: 400px; padding: 25px; border-radius: 16px; text-align: center; border: 1px solid var(--primary); }
        .modal-content h2 { color: var(--primary); margin-bottom: 15px; }
        .simulation-result { background: var(--bg-main); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .close-modal-btn { background: var(--bg-hover); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%; }

        @media (max-width: 768px) {
            .main-container { flex-direction: column; }
            .trade-panel { width: 100%; height: 45%; border-left: none; border-top: 1px solid var(--bg-hover); }
            #chart-view { height: 55%; }
        }
    </style>
</head>
<body>

    <div class="header">
        <div class="logo">Groww Pro <span class="tag">Paper</span></div>
        <div class="wallet-info">
            <div class="w-item"><span class="lbl">Wallet</span><span class="val" id="wallet-balance">₹10,00,000</span></div>
            <div class="w-item"><span class="lbl">Live P&L</span><span class="val text-green" id="live-pnl">₹0.00</span></div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('dashboard')">Explore</div>
        <div class="tab" onclick="switchTab('fno')">F&O</div>
    </div>

    <div class="main-container">
        <div class="content-area">
            <!-- DASHBOARD -->
            <div id="dashboard-view">
                <div class="indices">
                    <div class="index-card" onclick="openChart('NIFTY 50', 22000)">
                        <h4>NIFTY 50</h4><h2>22,000.00</h2>
                    </div>
                    <div class="index-card" onclick="openChart('SENSEX', 73000)">
                        <h4>SENSEX</h4><h2>73,000.00</h2>
                    </div>
                </div>
                <h3 style="font-size: 16px; margin-bottom: 15px; color: var(--text-muted);">Top 20 Companies</h3>
                <div class="stock-list" id="stock-list"></div>
            </div>

            <!-- F&O -->
            <div id="fno-view" style="display: none; padding: 15px;">
                <h3 style="font-size: 16px; margin-bottom: 15px; color: var(--text-muted);">NIFTY Futures & Options</h3>
                <div id="fno-list" style="display: flex; flex-direction: column; gap: 10px;"></div>
            </div>

            <!-- CHART VIEW -->
            <div id="chart-view">
                <div class="chart-header">
                    <button class="back-btn" onclick="closeChart()">←</button>
                    <h2 id="chart-title" style="font-size: 16px;">NIFTY 50</h2>
                    <button class="btn" onclick="showSimulation()" style="background: var(--green); color: white; border: none;">Simulate ₹5000</button>
                </div>
                <div class="toolbar">
                    <div class="btn-group">
                        <button class="btn active" onclick="toggleChartType('candle', this)">Candles</button>
                        <button class="btn" onclick="toggleChartType('line', this)">Line</button>
                    </div>
                </div>
                <div class="canvas-container" id="canvas-container">
                    <canvas id="tradeCanvas"></canvas>
                </div>
            </div>
        </div>

        <!-- TRADE PANEL -->
        <div class="trade-panel">
            <div class="panel-section">
                <div class="panel-title">Place Order</div>
                <div class="input-group"><label>Quantity</label><input type="number" id="trade-qty" value="10"></div>
                <div class="input-group"><label>Note</label><input type="text" id="trade-note" placeholder="Why trade?"></div>
                <div class="action-btns">
                    <button class="btn-action btn-buy" onclick="placeOrder('BUY')">BUY</button>
                    <button class="btn-action btn-sell" onclick="placeOrder('SELL')">SELL</button>
                </div>
            </div>
            <div class="panel-section" style="flex: 1;">
                <div class="panel-title">Open Positions</div>
                <div id="open-positions"><div style="text-align: center; color: var(--text-muted); font-size: 13px; margin-top: 20px;">No open positions</div></div>
            </div>
        </div>
    </div>

    <!-- MODAL -->
    <div class="modal-overlay" id="simulation-modal">
        <div class="modal-content">
            <h2>Profit Simulation</h2>
            <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 15px;">If you had invested ₹5,000 at the start...</p>
            <div class="simulation-result">
                <h3 id="sim-profit" class="text-green">+ ₹0.00</h3>
                <p id="sim-percent" style="font-size: 14px; font-weight: 600;">(0.00%)</p>
            </div>
            <button class="close-modal-btn" onclick="closeModal()">Close</button>
        </div>
    </div>

    <script>
        // --- DATA ---
        const companies = [
            { name: "Reliance", price: 2950 }, { name: "TCS", price: 3850 },
            { name: "HDFC Bank", price: 1500 }, { name: "ICICI Bank", price: 1120 },
            { name: "Infosys", price: 1620 }, { name: "Bharti Airtel", price: 1230 },
            { name: "SBI", price: 810 }, { name: "ITC", price: 435 },
            { name: "L&T", price: 3550 }, { name: "Kotak Bank", price: 1720 },
            { name: "Maruti Suzuki", price: 10500 }, { name: "Tata Motors", price: 950 },
            { name: "Titan", price: 3350 }, { name: "Sun Pharma", price: 1450 },
            { name: "Bajaj Finance", price: 7100 }, { name: "HCL Tech", price: 1420 },
            { name: "Axis Bank", price: 1100 }, { name: "Hindustan Unilever", price: 2450 },
            { name: "LIC", price: 920 }, { name: "Power Grid", price: 280 }
        ];

        let state = { balance: 1000000, positions: [] };
        let currentSymbol = "NIFTY 50", currentPrice = 22000;
        let chartData = [];
        let chartType = 'candle';
        let isChartOpen = false;

        // --- CANVAS SETUP ---
        const canvas = document.getElementById('tradeCanvas');
        const ctx = canvas.getContext('2d');
        const container = document.getElementById('canvas-container');

        function resizeCanvas() {
            if(!container.clientWidth || !container.clientHeight) return;
            // High-DPI rendering
            const dpr = window.devicePixelRatio || 1;
            canvas.width = container.clientWidth * dpr;
            canvas.height = container.clientHeight * dpr;
            ctx.scale(dpr, dpr);
            if(isChartOpen) drawChart();
        }
        window.addEventListener('resize', resizeCanvas);

        // --- INIT DASHBOARD ---
        function initDashboard() {
            const list = document.getElementById('stock-list');
            companies.forEach(c => {
                let div = document.createElement('div');
                div.className = 'stock-item';
                div.onclick = () => openChart(c.name, c.price);
                div.innerHTML = `<div class="stock-details"><h3>${c.name}</h3></div><div class="stock-price"><h3>₹${c.price.toFixed(2)}</h3></div>`;
                list.appendChild(div);
            });
            updateWalletUI();
        }

        // --- INIT F&O ---
        function initFNO() {
            const list = document.getElementById('fno-list');
            [21900, 21950, 22000, 22050, 22100].forEach(s => {
                let div = document.createElement('div');
                div.className = 'stock-item';
                div.innerHTML = `<div class="stock-details"><h3>NIFTY ${s} CE</h3></div><div class="stock-price"><h3>₹${(Math.random()*100+50).toFixed(2)}</h3></div>`;
                list.appendChild(div);
            });
        }

        // --- CHART LOGIC ---
        function generateData(count, startPrice) {
            let data = [];
            let price = startPrice;
            for(let i=0; i<count; i++) {
                let open = price;
                let close = price + (Math.random() - 0.48) * (startPrice * 0.01);
                let high = Math.max(open, close) + Math.random() * (startPrice * 0.005);
                let low = Math.min(open, close) - Math.random() * (startPrice * 0.005);
                data.push({ open, high, low, close });
                price = close;
            }
            return data;
        }

        function openChart(name, basePrice) {
            currentSymbol = name;
            document.getElementById('chart-title').innerText = name;
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('fno-view').style.display = 'none';
            document.getElementById('chart-view').style.display = 'flex';
            
            isChartOpen = true;
            chartData = generateData(60, basePrice);
            currentPrice = chartData[chartData.length - 1].close;

            // Resize after display block
            setTimeout(() => { resizeCanvas(); drawChart(); }, 10);
        }

        function closeChart() {
            isChartOpen = false;
            document.getElementById('chart-view').style.display = 'none';
            document.getElementById('dashboard-view').style.display = 'block';
        }

        function toggleChartType(type, btn) {
            document.querySelectorAll('.toolbar .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            chartType = type;
            drawChart();
        }

        // --- PURE CANVAS DRAWING ---
        function drawChart() {
            if(!canvas || !ctx || chartData.length === 0) return;
            
            const w = canvas.width / (window.devicePixelRatio || 1);
            const h = canvas.height / (window.devicePixelRatio || 1);
            
            ctx.clearRect(0, 0, w, h);
            
            let padding = 40;
            let chartW = w - padding;
            let chartH = h - padding * 2;

            // Find Min/Max
            let minP = Math.min(...chartData.map(d => d.low));
            let maxP = Math.max(...chartData.map(d => d.high));
            let range = maxP - minP;
            if(range === 0) range = 1;

            // Draw Grid & Y-Axis
            ctx.strokeStyle = '#1e293b';
            ctx.fillStyle = '#94a3b8';
            ctx.font = '12px Inter';
            ctx.lineWidth = 1;
            
            for(let i=0; i<=4; i++) {
                let y = padding + (i * chartH / 4);
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(chartW, y); ctx.stroke();
                ctx.fillText((maxP - i * range / 4).toFixed(2), chartW + 5, y + 4);
            }

            // Draw Candle or Line
            let cw = chartW / chartData.length;
            
            if(chartType === 'candle') {
                chartData.forEach((d, i) => {
                    let x = i * cw + cw / 2;
                    let yO = padding + chartH - ((d.open - minP) / range) * chartH;
                    let yC = padding + chartH - ((d.close - minP) / range) * chartH;
                    let yH = padding + chartH - ((d.high - minP) / range) * chartH;
                    let yL = padding + chartH - ((d.low - minP) / range) * chartH;

                    let color = d.close >= d.open ? '#10b981' : '#ef4444';
                    
                    // Wick
                    ctx.beginPath(); ctx.moveTo(x, yH); ctx.lineTo(x, yL); ctx.strokeStyle = color; ctx.stroke();
                    
                    // Body
                    ctx.fillStyle = color;
                    let bW = cw * 0.7;
                    let bH = Math.max(Math.abs(yO - yC), 2);
                    ctx.fillRect(x - bW/2, Math.min(yO, yC), bW, bH);
                });
            } else {
                ctx.beginPath();
                ctx.strokeStyle = '#3b82f6';
                ctx.lineWidth = 2;
                chartData.forEach((d, i) => {
                    let x = i * cw + cw / 2;
                    let y = padding + chartH - ((d.close - minP) / range) * chartH;
                    if(i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.stroke();
            }
        }

        // --- LIVE UPDATE ---
        setInterval(() => {
            if(!isChartOpen || chartData.length === 0) return;
            let last = chartData[chartData.length - 1];
            last.close += (Math.random() - 0.5) * (currentPrice * 0.002);
            last.high = Math.max(last.high, last.close);
            last.low = Math.min(last.low, last.close);
            currentPrice = last.close;
            
            drawChart();
            updatePnl();
        }, 2000);

        // --- TRADING ---
        function placeOrder(type) {
            if(!isChartOpen) return alert("Open a chart first!");
            let qty = parseFloat(document.getElementById('trade-qty').value);
            let note = document.getElementById('trade-note').value;
            if(!qty || !note) return alert("Enter qty and note!");

            state.positions.push({ id: Date.now(), symbol: currentSymbol, type, qty, entry: currentPrice, note });
            document.getElementById('trade-note').value = "";
            updatePositionsUI(); updatePnl();
        }

        function closePosition(id) {
            let idx = state.positions.findIndex(p => p.id === id);
            if(idx === -1) return;
            let p = state.positions[idx];
            let pnl = (p.type === 'BUY' ? (currentPrice - p.entry) : (p.entry - currentPrice)) * p.qty;
            state.balance += pnl;
            state.positions.splice(idx, 1);
            updateWalletUI(); updatePositionsUI(); updatePnl();
            alert(`Closed! P&L: ₹${pnl.toFixed(2)}`);
        }

        function updateWalletUI() { document.getElementById('wallet-balance').innerText = `₹${state.balance.toLocaleString('en-IN')}`; }

        function updatePnl() {
            let total = 0;
            state.positions.forEach(p => { total += (p.type === 'BUY' ? (currentPrice - p.entry) : (p.entry - currentPrice)) * p.qty; });
            let el = document.getElementById('live-pnl');
            el.innerText = `₹${total.toFixed(2)}`;
            el.className = "val " + (total >= 0 ? "text-green" : "text-red");
        }

        function updatePositionsUI() {
            let container = document.getElementById('open-positions');
            if(state.positions.length === 0) { container.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 13px; margin-top: 20px;">No open positions</div>`; return; }
            container.innerHTML = "";
            state.positions.forEach(p => {
                let pnl = (p.type === 'BUY' ? (currentPrice - p.entry) : (p.entry - currentPrice)) * p.qty;
                container.innerHTML += `
                    <div class="pos-card">
                        <div class="pos-header"><span class="${p.type === 'BUY' ? 'text-green' : 'text-red'}">${p.type} ${p.qty}</span><span class="${pnl >= 0 ? 'text-green' : 'text-red'}">₹${pnl.toFixed(2)}</span></div>
                        <div style="font-size: 12px; color: var(--text-muted);">${p.symbol} @ ₹${p.entry.toFixed(2)}</div>
                        <button class="btn-close" onclick="closePosition(${p.id})">Close</button>
                    </div>`;
            });
        }

        // --- MODAL ---
        function showSimulation() {
            if(!isChartOpen || chartData.length < 2) return;
            let start = chartData[0].close, end = chartData[chartData.length-1].close;
            let shares = 5000 / start;
            let profit = (shares * end) - 5000;
            let percent = (profit / 5000) * 100;
            
            let el = document.getElementById('sim-profit'), pel = document.getElementById('sim-percent');
            el.innerText = (profit >= 0 ? "+ ₹" : "- ₹") + Math.abs(profit).toFixed(2);
            el.className = profit >= 0 ? "text-green" : "text-red";
            pel.innerText = `(${percent >= 0 ? "+" : ""}${percent.toFixed(2)}%)`;
            pel.style.color = profit >= 0 ? 'var(--green)' : 'var(--red)';
            document.getElementById('simulation-modal').style.display = 'flex';
        }
        function closeModal() { document.getElementById('simulation-modal').style.display = 'none'; }
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('dashboard-view').style.display = tab === 'dashboard' ? 'block' : 'none';
            document.getElementById('fno-view').style.display = tab === 'fno' ? 'block' : 'none';
            document.getElementById('chart-view').style.display = 'none';
        }

        window.onload = () => { initDashboard(); initFNO(); };
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_CODE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
