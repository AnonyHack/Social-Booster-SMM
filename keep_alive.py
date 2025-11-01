import os
import time
import requests
import logging
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            port = self.server.server_port
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>SMM Bot - Social Media Marketing</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: #333;
                        min-height: 100vh;
                    }}
                    .container {{
                        background: rgba(255, 255, 255, 0.95);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                        margin-top: 20px;
                    }}
                    h1 {{
                        text-align: center;
                        margin-bottom: 10px;
                        font-size: 3em;
                        color: #764ba2;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                    }}
                    .tagline {{
                        text-align: center;
                        font-size: 1.3em;
                        color: #667eea;
                        margin-bottom: 30px;
                        font-style: italic;
                    }}
                    .status-card {{
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        padding: 25px;
                        margin: 20px 0;
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                    }}
                    .status-badge {{
                        display: inline-block;
                        padding: 10px 25px;
                        border-radius: 25px;
                        font-weight: bold;
                        font-size: 1.2em;
                        background: rgba(255, 255, 255, 0.2);
                        margin-bottom: 15px;
                    }}
                    .info-grid {{
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                        margin-top: 30px;
                    }}
                    .info-item {{
                        background: rgba(255, 255, 255, 0.8);
                        padding: 20px;
                        border-radius: 12px;
                        border-left: 4px solid #667eea;
                    }}
                    .feature-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 15px;
                        margin-top: 20px;
                    }}
                    .feature-item {{
                        background: linear-gradient(135deg, #f093fb, #f5576c);
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        box-shadow: 0 5px 15px rgba(245, 87, 108, 0.3);
                    }}
                    .social-icon {{
                        font-size: 2em;
                        margin-bottom: 10px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        color: #636e72;
                    }}
                    h3 {{
                        color: #2d3436;
                        border-bottom: 2px solid #667eea;
                        padding-bottom: 10px;
                    }}
                    .stats {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                        margin: 20px 0;
                    }}
                    .stat-item {{
                        background: linear-gradient(135deg, #4facfe, #00f2fe);
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 SMM Bot - Social Booster</h1>
                    <div class="tagline">Premium Social Media Marketing Services</div>
                    
                    <div class="status-card">
                        <div class="status-badge">
                            🟢 ONLINE & RUNNING
                        </div>
                        <p><strong>Last Updated:</strong> {current_time}</p>
                        <p><strong>Server:</strong> Render • <strong>Port:</strong> {port}</p>
                        <p><strong>Status:</strong> Operational & Ready to Serve</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-item">
                            <div class="social-icon">📊</div>
                            <h3>50+ Services</h3>
                            <p>Wide range of SMM services</p>
                        </div>
                        <div class="stat-item">
                            <div class="social-icon">⚡</div>
                            <h3>Fast Delivery</h3>
                            <p>Quick order processing</p>
                        </div>
                        <div class="stat-item">
                            <div class="social-icon">🛡️</div>
                            <h3>Secure</h3>
                            <p>Safe transactions</p>
                        </div>
                        <div class="stat-item">
                            <div class="social-icon">📱</div>
                            <h3>24/7 Support</h3>
                            <p>Always available</p>
                        </div>
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-item">
                            <h3>🤖 Bot Features</h3>
                            <p><strong>Platform:</strong> Telegram Bot</p>
                            <p><strong>Type:</strong> SMM Services</p>
                            <p><strong>Payment:</strong> Multiple Methods</p>
                            <p><strong>Support:</strong> Admin Panel</p>
                        </div>
                        
                        <div class="info-item">
                            <h3>🔧 Technical Info</h3>
                            <p><strong>Server:</strong> Render Cloud</p>
                            <p><strong>Port:</strong> {port}</p>
                            <p><strong>Health Check:</strong> Active</p>
                            <p><strong>Uptime:</strong> 99.9%</p>
                        </div>
                    </div>
                    
                    <div class="info-item">
                        <h3>📱 Supported Platforms</h3>
                        <div class="feature-grid">
                            <div class="feature-item">
                                <div class="social-icon">📷</div>
                                <h4>Instagram</h4>
                                <p>Followers, Likes, Views</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">📘</div>
                                <h4>Facebook</h4>
                                <p>Likes, Shares, Followers</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">🐦</div>
                                <h4>Twitter</h4>
                                <p>Followers, Retweets, Likes</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">📺</div>
                                <h4>YouTube</h4>
                                <p>Views, Subscribers, Likes</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">💬</div>
                                <h4>Telegram</h4>
                                <p>Members, Views, Reactions</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">👥</div>
                                <h4>TikTok</h4>
                                <p>Followers, Likes, Views</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-item">
                        <h3>⭐ Premium Services</h3>
                        <div class="feature-grid">
                            <div class="feature-item">
                                <div class="social-icon">🚀</div>
                                <h4>Instant Delivery</h4>
                                <p>Fast service activation</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">⭐</div>
                                <h4>High Quality</h4>
                                <p>Premium quality services</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">🛡️</div>
                                <h4>Safe & Secure</h4>
                                <p>Guaranteed safety</p>
                            </div>
                            <div class="feature-item">
                                <div class="social-icon">📞</div>
                                <h4>24/7 Support</h4>
                                <p>Always here to help</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>⚡ Powered by SMM Bot Technology</p>
                        <p>🌐 Running on Render Cloud Platform</p>
                        <p style="margin-top: 10px; font-size: 0.9em;">
                            "Boost your social media presence with our premium services 🚀"
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 - Page not found")
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        logger.info(f"HTTP {self.command} {self.path} - {self.client_address[0]}")

def run_health_server(port=10000):
    """Run the health server with website feature"""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"Health server started successfully on port {port}")
        logger.info(f"SMM Bot status page: http://0.0.0.0:{port}/")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")
        raise

def keep_alive(port=10000):
    """Pings the server periodically to prevent shutdown"""
    session = requests.Session()
    
    while True:
        try:
            # Ping our own health endpoint
            session.get(f'http://localhost:{port}/ping', timeout=5)
            logger.debug(f"Keep-alive ping sent to localhost:{port}")
        except Exception as e:
            logger.warning(f"Keep-alive ping to localhost:{port} failed: {e}")
        
        try:
            # Optionally ping external services
            session.get('https://www.google.com', timeout=5)
            logger.debug("Keep-alive ping sent to external service")
        except Exception as e:
            logger.warning(f"Keep-alive ping to external service failed: {e}")
        
        time.sleep(300)  # Ping every 5 minutes

def start_keep_alive(port=10000):
    """Start the keep-alive system in separate threads"""
    # Start health server thread
    health_thread = Thread(target=run_health_server, args=(port,), daemon=True)
    health_thread.start()
    logger.info(f"Health server started on port {port}")
    
    # Start keep-alive ping thread
    ping_thread = Thread(target=keep_alive, args=(port,), daemon=True)
    ping_thread.start()
    logger.info(f"Keep-alive ping system started")
    
    return health_thread, ping_thread
