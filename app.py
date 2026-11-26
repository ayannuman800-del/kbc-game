from flask import Flask, render_template_string

app = Flask(__name__)

# ==========================================
# GROWW PRO - ULTIMATE PAPER TRADING
# ==========================================
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Groww Pro | Paper Trading</title>
    
    <!-- TradingView Official Chart Library -->
    <script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
    
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
        
        /* --- HEADER --- */
        .header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); z-index: 100; }
        .logo { font-size: 20px; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 8px; }
        .tag { font-size: 10px; background: var(--primary); color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
        
        .wallet-info { display: flex; gap: 20px; }
        .w-item { display: flex; flex-direction: column; align-items: flex-end; }
        .w-item .lbl { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .w-item .val { font-size: 16px; font-weight: 600; }
        .text-green { color: var(--green) !important; }
        .text-red { color: var(--red) !important; }

        /* --- LAYOUT --- */
        .main-container { display: flex; flex: 1; overflow: hidden; }
        
        /* --- TABS --- */
        .tabs { display: flex; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); }
        .tab { flex: 1; text-align: center; padding: 12px; cursor: pointer; font-size: 14px; font-weight: 500; color: var(--text-muted); border-bottom: 2px solid transparent; transition: 0.3s; }
        .tab.active { color: var(--primary); border-bottom: 2px solid var(--primary); background: rgba(59, 130, 246, 0.05); }
        
        .content-area { flex: 1; display: flex; flex-direction: column; position: relative; overflow: hidden; }

        /* --- DASHBOARD VIEW --- */
        #dashboard-view { padding: 15px; overflow-y: auto; height: 100%; }
        .indices { display: flex; gap: 15px; margin-bottom: 20px; }
        .index-card { flex: 1; background: var(--bg-card); border: 1px solid var(--bg-hover); border-radius: 12px; padding: 15px; cursor: pointer; transition: 0.2s; }
        .index-card:hover { border-color: var(--primary); transform: translateY(-2px); }
        .index-card h4 { font-size: 14px; color: var(--text-muted); margin-bottom: 8px; }
        .index-card h2 { font-size: 22px; font-weight: 700; }
        
        .stock-list { display: flex; flex-direction: column; gap: 10px; }
        .stock-item { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); padding: 15px; border-radius: 10px; border: 1px solid var(--bg-hover); cursor: pointer; transition: 0.2s; }
        .stock-item:hover { background: var(--bg-hover); }
        .stock-details h3 { font-size: 15px; font-weight: 600; }
        .stock-details p { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
        .stock-price { text-align: right; }
        .stock-price h3 { font-size: 15px; font-weight: 600; }
        .stock-price p { font-size: 12px; font-weight: 500; margin-top: 4px; }

        /* --- CHART VIEW --- */
        #chart-view { display: none; flex-direction: column; height: 100%; background: var(--bg-main); }
        .chart-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); }
        .back-btn { background: none; border: none; color: var(--text-main); font-size: 20px; cursor: pointer; }
        
        .toolbar { display: flex; gap: 10px; padding: 10px 15px; background: var(--bg-card); border-bottom: 1px solid var(--bg-hover); align-items: center; overflow-x: auto; }
        .btn-group { display: flex; gap: 5px; }
        .btn { padding: 6px 12px; border: 1px solid var(--bg-hover); background: var(--bg-main); color: var(--text-muted); border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; white-space: nowrap;}
        .btn.active { background: var(--primary); color: white; border-color: var(--primary); }
        
        #tv-chart { flex: 1; width: 100%; min-height: 350px; position: relative; }

        /* --- F&O VIEW --- */
        #fno-view { padding: 15px; overflow-y: auto; display: none; }
        .fno-table { width: 100%; border-collapse: collapse; background: var(--bg-card); border-radius: 12px; overflow: hidden; }
        .fno-table th, .fno-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--bg-hover); }
        .fno-table th { color: var(--text-muted); font-size: 12px; font-weight: 500; }
        .fno-table td { font-size: 14px; font-weight: 500; }
        .btn-trade-small { padding: 4px 10px; border-radius: 4px; border: none; color: white; cursor: pointer; font-size: 12px; font-weight: 600; }
        
        /* --- TRADE PANEL (SIDEBAR) --- */
        .trade-panel { width: 320px; background: var(--bg-card); border-left: 1px solid var(--bg-hover); display: flex; flex-direction: column; overflow-y: auto; }
        .panel-section { padding: 15px; border-bottom: 1px solid var(--bg-hover); }
        .panel-title { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }
        
        .input-group { margin-bottom: 12px; }
        .input-group label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
        .input-group input { width: 100%; padding: 10px; background: var(--bg-main); border: 1px solid var(--bg-hover); color: var(--text-main); border-radius: 8px; font-size: 14px; outline: none; transition: 0.2s; }
        .input-group input:focus { border-color: var(--primary); }
        
        .action-btns { display: flex; gap: 10px; }
        .btn-action { flex: 1; padding: 12px; border: none; border-radius: 8px; font-weight: 700; font-size: 15px; color: white; cursor: pointer; transition: 0.2s; }
        .btn-buy { background: var(--green); }
        .btn-sell { background: var(--red); }
        .btn-action:active { transform: scale(0.98); }

        /* --- POSITIONS --- */
        .pos-card { background: var(--bg-main); border: 1px solid var(--bg-hover); padding: 12px; border-radius: 8px; margin-bottom: 10px; }
        .pos-header { display: flex; justify-content: space-between; font-weight: 600; font-size: 14px; margin-bottom: 8px; }
        .pos-details { font-size: 12px; color: var(--text-muted); margin-bottom: 8px; display: flex; justify-content: space-between;}
        .btn-close { width: 100%; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--red); color: var(--red); padding: 8px; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer; transition: 0.2s;}
        .btn-close:hover { background: var(--red); color: white; }

        /* --- SIMULATION MODAL --- */
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(5px); }
        .modal-content { background: var(--bg-card); width: 90%; max-width: 400px; padding: 25px; border-radius: 16px; border: 1px solid var(--primary); text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .modal-content h2 { color: var(--primary); margin-bottom: 15px; }
        .simulation-result { background: var(--bg-main); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .simulation-result h3 { font-size: 24px; margin-bottom: 5px; }
        .close-modal-btn { background: var(--bg-hover); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; width: 100%; }

        @media (max-width: 768px) {
            .main-container { flex-direction: column; }
            .trade-panel { width: 100%; height: 45%; border-left: none; border-top: 1px solid var(--bg-hover); }
            #chart-view { height: 55%; }
            .indices { flex-direction: column; }
        }
    </style>
</head>
<body>

    <!-- HEADER -->
    <div class="header">
        <div class="logo">Groww Pro <span class="tag">Paper</span></div>
        <div class="wallet-info">
            <div class="w-item">
                <span class="lbl">Wallet</span>
                <span class="val" id="wallet-balance">₹10,00,000</span>
            </div>
            <div class="w-item">
                <span class="lbl">Live P&L</span>
                <span class="val text-green" id="live-pnl">₹0.00</span>
            </div>
        </div>
    </div>

    <!-- TABS -->
    <div class="tabs">
        <div class="tab active" onclick="switchTab('dashboard')">Explore</div>
        <div class="tab" onclick="switchTab('fno')">F&O</div>
        <div class="tab" onclick="switchTab('positions')">Positions</div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="main-container">
        
        <div class="content-area">
            <!-- 1. DASHBOARD VIEW -->
            <div id="dashboard-view">
                <div class="indices">
                    <div class="index-card" onclick="openChart('NIFTY 50', 22000)">
                        <h4>NIFTY 50</h4>
                        <h2 id="nifty-price">22,000.00</h2>
                    </div>
                    <div class="index-card" onclick="openChart('SENSEX', 73000)">
                        <h4>SENSEX</h4>
                        <h2 id="sensex-price">73,000.00</h2>
                    </div>
                </div>
                
                <h3 style="font-size: 16px; margin-bottom: 15px; color: var(--text-muted);">Top Companies</h3>
                <div class="stock-list" id="stock-list">
                    <!-- Populated by JS -->
                </div>
            </div>

            <!-- 2. F&O VIEW -->
            <div id="fno-view">
                <h3 style="font-size: 16px; margin-bottom: 15px; color: var(--text-muted);">NIFTY Futures & Options</h3>
                <table class="fno-table">
                    <thead>
                        <tr>
                            <th>Instrument</th>
                            <th>LTP</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="fno-body">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>

            <!-- 3. CHART VIEW -->
            <div id="chart-view">
                <div class="chart-header">
                    <button class="back-btn" onclick="closeChart()">←</button>
                    <h2 id="chart-title" style="font-size: 16px;">NIFTY 50</h2>
                    <button class="btn" onclick="showSimulation()" style="background: var(--green); color: white; border: none;">Simulate ₹5000</button>
                </div>
                <div class="toolbar">
                    <div class="btn-group">
                        <button class="btn" onclick="changeTF('1m', this)">1m</button>
                        <button class="btn" onclick="changeTF('5m', this)">5m</button>
                        <button class="btn active" onclick="changeTF('10m', this)">10m</button>
                        <button class="btn" onclick="changeTF('1D', this)">1D</button>
                    </div>
                    <div class="btn-group" style="margin-left: 10px;">
                        <button class="btn active" onclick="toggleChartType('candle', this)">Candles</button>
                        <button class="btn" onclick="toggleChartType('line', this)">Line</button>
                    </div>
                </div>
                <div id="tv-chart"></div>
            </div>
        </div>

        <!-- TRADE PANEL (Right Side) -->
        <div class="trade-panel">
            <div class="panel-section">
                <div class="panel-title">Place Order</div>
                <div class="input-group">
                    <label>Quantity</label>
                    <input type="number" id="trade-qty" value="10" min="1">
                </div>
                <div class="input-group">
                    <label>Trade Note (Why?)</label>
                    <input type="text" id="trade-note" placeholder="e.g. Support Breakout">
                </div>
                <div class="action-btns">
                    <button class="btn-action btn-buy" onclick="placeOrder('BUY')">BUY</button>
                    <button class="btn-action btn-sell" onclick="placeOrder('SELL')">SELL</button>
                </div>
            </div>

            <div class="panel-section" style="flex: 1;">
                <div class="panel-title">Open Positions</div>
                <div id="open-positions">
                    <div style="text-align: center; color: var(--text-muted); font-size: 13px; margin-top: 20px;">No open positions</div>
                </div>
            </div>
        </div>

    </div>

    <!-- SIMULATION MODAL -->
    <div class="modal-overlay" id="simulation-modal">
        <div class="modal-content">
            <h2>Profit Simulation</h2>
            <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 15px;">If you had invested ₹5,000 at the start of this chart...</p>
            <div class="simulation-result">
                <h3 id="sim-profit" class="text-green">+ ₹0.00</h3>
                <p id="sim-percent" style="font-size: 14px; font-weight: 600;">(0.00%)</p>
            </div>
            <button class="close-modal-btn" onclick="closeModal()">Close</button>
        </div>
    </div>

    <script>
        // --- DATA & STATE ---
        const companies = [
            { name: "Reliance", symbol: "RELIANCE", price: 2950 },
            { name: "TCS", symbol: "TCS", price: 3850 },
            { name: "HDFC Bank", symbol: "HDFCBANK", price: 1500 },
            { name: "ICICI Bank", symbol: "ICICIBANK", price: 1120 },
            { name: "Infosys", symbol: "INFY", price: 1620 },
            { name: "Bharti Airtel", symbol: "BHARTIARTL", price: 1230 },
            { name: "SBI", symbol: "SBIN", price: 810 },
            { name: "ITC", symbol: "ITC", price: 435 },
            { name: "L&T", symbol: "LT", price: 3550 },
            { name: "Kotak Bank", symbol: "KOTAKBANK", price: 1720 },
            { name: "Maruti Suzuki", symbol: "MARUTI", price: 10500 },
            { name: "Tata Motors", symbol: "TATAMOTORS", price: 950 },
            { name: "Titan", symbol: "TITAN", price: 3350 },
            { name: "Sun Pharma", symbol: "SUNPHARMA", price: 1450 },
            { name: "Bajaj Finance", symbol: "BAJFINANCE", price: 7100 },
            { name: "HCL Tech", symbol: "HCLTECH", price: 1420 },
            { name: "Axis Bank", symbol: "AXISBANK", price: 1100 },
            { name: "Hindustan Unilever", symbol: "HINDUNILVR", price: 2450 },
            { name: "LIC", symbol: "LICI", price: 920 },
            { name: "Power Grid", symbol: "POWERGRID", price: 280 }
        ];

        let state = {
            balance: 1000000,
            positions: []
        };

        let currentSymbol = "NIFTY 50";
        let currentPrice = 22000;
        let chartData = [];
        let isChartOpen = false;
        let chartType = 'candle';

        // --- CHART INIT ---
        const chartContainer = document.getElementById('tv-chart');
        const chart = LightweightCharts.createChart(chartContainer, {
            layout: { background: { color: '#0f172a' }, textColor: '#94a3b8' },
            grid: { vertLines: { color: '#1e293b' }, horzLines: { color: '#1e293b' } },
            crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
            timeScale: { timeVisible: true, secondsVisible: false, borderColor: '#334155' },
        });

        const candleSeries = chart.addCandlestickSeries({
            upColor: '#10b981', downColor: '#ef4444', borderVisible: false,
            wickUpColor: '#10b981', wickDownColor: '#ef4444'
        });

        const lineSeries = chart.addLineSeries({ color: '#3b82f6', lineWidth: 2, visible: false });

        // --- INIT DASHBOARD ---
        function initDashboard() {
            const list = document.getElementById('stock-list');
            companies.forEach(c => {
                let div = document.createElement('div');
                div.className = 'stock-item';
                div.onclick = () => openChart(c.name, c.price);
                div.innerHTML = `
                    <div class="stock-details">
                        <h3>${c.name}</h3>
                        <p>NSE • Equity</p>
                    </div>
                    <div class="stock-price">
                        <h3>₹${c.price.toFixed(2)}</h3>
                        <p class="text-green">+${(Math.random()*2).toFixed(2)}%</p>
                    </div>
                `;
                list.appendChild(div);
            });
            updateWalletUI();
        }

        function initFNO() {
            const tbody = document.getElementById('fno-body');
            const strikes = [21900, 21950, 22000, 22050, 22100];
            strikes.forEach(s => {
                let tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><b>NIFTY ${s} CE</b><br><span style="font-size:10px; color:var(--text-muted);">Weekly Expiry</span></td>
                    <td class="text-green">₹${(Math.random()*100+50).toFixed(2)}</td>
                    <td><button class="btn-trade-small btn-buy" onclick="alert('F&O trading simulation active.')">BUY</button></td>
                `;
                tbody.appendChild(tr);
            });
        }

        // --- TABS ---
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('fno-view').style.display = 'none';
            document.getElementById('chart-view').style.display = 'none';

            if(tab === 'dashboard') document.getElementById('dashboard-view').style.display = 'block';
            if(tab === 'fno') document.getElementById('fno-view').style.display = 'block';
            if(tab === 'positions') {
                document.getElementById('dashboard-view').style.display = 'block';
                // Just showing dashboard but scrolling to positions is fine for now
            }
        }

        // --- CHART LOGIC ---
        function generateData(count, startPrice) {
            let data = [];
            let time = Math.floor(Date.now() / 1000) - (count * 600);
            let price = startPrice;
            for(let i=0; i<count; i++) {
                let open = price;
                let close = price + (Math.random() - 0.48) * (startPrice * 0.005);
                let high = Math.max(open, close) + Math.random() * (startPrice * 0.002);
                let low = Math.min(open, close) - Math.random() * (startPrice * 0.002);
                data.push({ time: time + i * 600, open, high, low, close });
                price = close;
            }
            return data;
        }

        function openChart(name, basePrice) {
            currentSymbol = name;
            currentPrice = basePrice;
            document.getElementById('chart-title').innerText = name;
            
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('fno-view').style.display = 'none';
            document.getElementById('chart-view').style.display = 'flex';
            
            chartData = generateData(100, basePrice);
            candleSeries.setData(chartData);
            lineSeries.setData(chartData.map(d => ({ time: d.time, value: d.close })));
            
            currentPrice = chartData[chartData.length - 1].close;
            chart.timeScale().fitContent();
        }

        function closeChart() {
            document.getElementById('chart-view').style.display = 'none';
            document.getElementById('dashboard-view').style.display = 'block';
        }

        function toggleChartType(type, btn) {
            document.querySelectorAll('.toolbar .btn-group:nth-child(2) .btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            chartType = type;
            
            if(type === 'candle') {
                candleSeries.applyOptions({ visible: true });
                lineSeries.applyOptions({ visible: false });
            } else {
                candleSeries.applyOptions({ visible: false });
                lineSeries.applyOptions({ visible: true });
            }
        }

        // --- LIVE UPDATE ---
        setInterval(() => {
            if(!isChartOpen || chartData.length === 0) return;
            
            let last = chartData[chartData.length - 1];
            last.close += (Math.random() - 0.5) * (currentPrice * 0.001);
            last.high = Math.max(last.high, last.close);
            last.low = Math.min(last.low, last.close);
            
            candleSeries.update(last);
            lineSeries.update({ time: last.time, value: last.close });
            currentPrice = last.close;
            
            updatePnl();
        }, 2000);

        // --- TRADING LOGIC ---
        function placeOrder(type) {
            if(!isChartOpen) return alert("Please open a stock chart first!");
            
            let qty = parseFloat(document.getElementById('trade-qty').value);
            let note = document.getElementById('trade-note').value;
            
            if(!qty || qty <= 0) return alert("Enter valid quantity!");
            if(!note) return alert("Please write a trade note!");

            state.positions.push({
                id: Date.now(),
                symbol: currentSymbol,
                type: type,
                qty: qty,
                entry: currentPrice,
                note: note
            });

            document.getElementById('trade-note').value = "";
            updatePositionsUI();
            updatePnl();
        }

        function closePosition(id) {
            let idx = state.positions.findIndex(p => p.id === id);
            if(idx === -1) return;
            
            let p = state.positions[idx];
            let exitPrice = (p.symbol === currentSymbol) ? currentPrice : p.entry; // Simplified exit price
            let pnl = (p.type === 'BUY' ? (exitPrice - p.entry) : (p.entry - exitPrice)) * p.qty;
            
            state.balance += pnl;
            state.positions.splice(idx, 1);
            
            updateWalletUI();
            updatePositionsUI();
            updatePnl();
            alert(`Position Closed! P&L: ₹${pnl.toFixed(2)}`);
        }

        function updateWalletUI() {
            document.getElementById('wallet-balance').innerText = `₹${state.balance.toLocaleString('en-IN', {maximumFractionDigits: 2})}`;
        }

        function updatePnl() {
            let total = 0;
            state.positions.forEach(p => {
                let currentStockPrice = (p.symbol === currentSymbol) ? currentPrice : p.entry;
                total += (p.type === 'BUY' ? (currentStockPrice - p.entry) : (p.entry - currentStockPrice)) * p.qty;
            });
            
            let el = document.getElementById('live-pnl');
            el.innerText = `₹${total.toFixed(2)}`;
            el.className = "val " + (total >= 0 ? "text-green" : "text-red");
        }

        function updatePositionsUI() {
            let container = document.getElementById('open-positions');
            if(state.positions.length === 0) {
                container.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 13px; margin-top: 20px;">No open positions</div>`;
                return;
            }
            
            container.innerHTML = "";
            state.positions.forEach(p => {
                let currentStockPrice = (p.symbol === currentSymbol) ? currentPrice : p.entry;
                let pnl = (p.type === 'BUY' ? (currentStockPrice - p.entry) : (p.entry - currentStockPrice)) * p.qty;
                
                container.innerHTML += `
                    <div class="pos-card">
                        <div class="pos-header">
                            <span class="${p.type === 'BUY' ? 'text-green' : 'text-red'}">${p.type} ${p.qty} Qty</span>
                            <span class="${pnl >= 0 ? 'text-green' : 'text-red'}">₹${pnl.toFixed(2)}</span>
                        </div>
                        <div class="pos-details">
                            <span>${p.symbol}</span>
                            <span>Entry: ₹${p.entry.toFixed(2)}</span>
                        </div>
                        <div style="font-size: 11px; color: var(--text-muted); font-style: italic; margin-bottom: 8px;">"${p.note}"</div>
                        <button class="btn-close" onclick="closePosition(${p.id})">Close Position</button>
                    </div>
                `;
            });
        }

        // --- SIMULATION LOGIC ---
        function showSimulation() {
            if(!isChartOpen || chartData.length < 2) return;
            
            let startPrice = chartData[0].close;
            let currentPrice = chartData[chartData.length - 1].close;
            
            let shares = 5000 / startPrice;
            let currentValue = shares * currentPrice;
            let profit = currentValue - 5000;
            let percent = (profit / 5000) * 100;
            
            let profitEl = document.getElementById('sim-profit');
            let percentEl = document.getElementById('sim-percent');
            
            profitEl.innerText = (profit >= 0 ? "+ " : "- ") + "₹" + Math.abs(profit).toFixed(2);
            profitEl.className = profit >= 0 ? "text-green" : "text-red";
            percentEl.innerText = `(${percent >= 0 ? "+" : ""}${percent.toFixed(2)}%)`;
            percentEl.style.color = profit >= 0 ? 'var(--green)' : 'var(--red)';
            
            document.getElementById('simulation-modal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('simulation-modal').style.display = 'none';
        }

        // --- INIT ---
        window.onload = () => {
            initDashboard();
            initFNO();
            window.addEventListener('resize', () => {
                if(isChartOpen) chart.resize(chartContainer.clientWidth, chartContainer.clientHeight);
            });
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
