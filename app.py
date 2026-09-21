from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Crypto Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-color: #0b0e14;
            color: #00ffcc;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            padding: 20px;
            margin: 0;
        }
        h1 { margin-bottom: 10px; text-shadow: 0 0 10px #00ffcc; }
        .controls {
            margin-bottom: 20px;
        }
        select {
            background: #151922;
            color: #00ffcc;
            border: 1px solid #00ffcc;
            padding: 8px 15px;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
        }
        .chart-container {
            width: 95%;
            max-width: 650px;
            margin: auto;
            background: #151922;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.15);
        }
        .price-badge {
            font-size: 24px;
            font-weight: bold;
            margin: 15px 0;
            color: #fff;
        }
    </style>
</head>
<body>

    <h1>🚀 Live Crypto Tracker</h1>
    
    <div class="controls">
        <label for="cryptoSelect">Select Coin: </label>
        <select id="cryptoSelect" onchange="updateChart()">
            <option value="bitcoin">Bitcoin (BTC)</option>
            <option value="ethereum">Ethereum (ETH)</option>
            <option value="dogecoin">Dogecoin (DOGE)</option>
        </select>
    </div>

    <div class="price-badge" id="currentPrice">Loading price...</div>

    <div class="chart-container">
        <canvas id="cryptoChart"></canvas>
    </div>

    <script>
        let myChart = null;

        async function updateChart() {
            const coin = document.getElementById('cryptoSelect').value;
            const res = await fetch(`/api/data?coin=${coin}`);
            const data = await res.json();

            // Price badge update
            const latestPrice = data.prices[data.prices.length - 1];
            document.getElementById('currentPrice').innerText = `$${latestPrice.toLocaleString()}`;

            const ctx = document.getElementById('cryptoChart').getContext('2d');

            if (myChart) {
                myChart.data.labels = data.labels;
                myChart.data.datasets[0].data = data.prices;
                myChart.data.datasets[0].label = `${coin.toUpperCase()} Price (USD)`;
                myChart.update();
            } else {
                myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: `${coin.toUpperCase()} Price (USD)`,
                            data: data.prices,
                            borderColor: '#00ffcc',
                            backgroundColor: 'rgba(0, 255, 204, 0.1)',
                            fill: true,
                            tension: 0.3,
                            pointRadius: 4,
                            pointHoverRadius: 7
                        }]
                    },
                    options: {
                        responsive: true,
                        animation: { duration: 1000 },
                        scales: {
                            x: { ticks: { color: '#888' }, grid: { color: '#222' } },
                            y: { ticks: { color: '#888' }, grid: { color: '#222' } }
                        }
                    }
                });
            }
        }

        // Initial load
        updateChart();

        // Auto-refresh every 10 seconds
        setInterval(updateChart, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    from flask import request
    coin = request.args.get('coin', 'bitcoin')
    
    # Live market data fetch from CoinGecko API
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=1&interval=hourly"
    
    try:
        response = requests.get(url, timeout=5).json()
        prices_raw = response.get('prices', [])[-10:]  # Last 10 hours data
        
        labels = []
        prices = []
        
        for p in prices_raw:
            # Convert timestamp to time (HH:MM)
            import datetime
            time_str = datetime.datetime.fromtimestamp(p[0]/1000).strftime('%H:%M')
            labels.append(time_str)
            prices.append(round(p[1], 2))
            
        return jsonify({"labels": labels, "prices": prices})
    except Exception as e:
        # Fallback if API rate limits
        return jsonify({
            "labels": ["10:00", "11:00", "12:00", "13:00"],
            "prices": [42000, 42500, 41800, 43100]
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
