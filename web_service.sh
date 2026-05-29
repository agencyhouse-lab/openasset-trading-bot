#!/bin/bash
# OpenAsset Web Admin Service
# Usage: bash web_service.sh [start|stop|status|install-service]
set -e

WEB_DIR="/root/openasset-trading-bot"
API_FILE="$WEB_DIR/web_api.py"
LOG="/var/log/openasset_web.log"
PID_FILE="/tmp/openasset_web.pid"
PORT="${OPENASSET_WEB_PORT:-8080}"
PASSWORD="${OPENASSET_WEB_PASSWORD:-openasset2026}"

cmd="${1:-start}"

case "$cmd" in

  start)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
      echo "✅ Web server already running (PID $(cat $PID_FILE))"
      echo "   http://72.62.254.237:$PORT"
      exit 0
    fi
    # Install deps if needed
    python3 -c "import fastapi, uvicorn" 2>/dev/null || \
      pip install fastapi uvicorn --break-system-packages -q
    cd "$WEB_DIR"
    echo "🔄 Starting OpenAsset Web Admin on port $PORT..."
    nohup python3 web_api.py > "$LOG" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 2
    if kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
      echo "✅ Web server started (PID $(cat $PID_FILE))"
      echo ""
      echo "  🌐 URL:       http://72.62.254.237:$PORT"
      echo "  🔑 Password:  $PASSWORD"
      echo "  📋 Logs:      tail -f $LOG"
      echo "  🛑 Stop:      bash web_service.sh stop"
    else
      echo "❌ Web server failed to start"
      tail -10 "$LOG"
      exit 1
    fi
    ;;

  stop)
    if [ -f "$PID_FILE" ]; then
      kill "$(cat $PID_FILE)" 2>/dev/null && echo "✅ Web server stopped" || echo "⚠️  Process not found"
      rm -f "$PID_FILE"
    else
      pkill -f "web_api.py" 2>/dev/null && echo "✅ Web server stopped" || echo "⚠️  Not running"
    fi
    ;;

  restart)
    bash "$0" stop
    sleep 1
    bash "$0" start
    ;;

  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
      echo "🟢 Web server RUNNING (PID $(cat $PID_FILE))"
      echo "   http://72.62.254.237:$PORT"
    else
      echo "🔴 Web server NOT running"
    fi
    ;;

  install-service)
    # Create systemd service for auto-start on reboot
    cat > /etc/systemd/system/openasset-web.service << SVC
[Unit]
Description=OpenAsset Web Admin Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$WEB_DIR
Environment=OPENASSET_WEB_PASSWORD=$PASSWORD
Environment=OPENASSET_WEB_PORT=$PORT
ExecStart=/usr/bin/python3 $API_FILE
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SVC
    systemctl daemon-reload
    systemctl enable openasset-web
    systemctl start openasset-web
    echo "✅ Systemd service installed and started"
    echo "   systemctl status openasset-web"
    ;;

  *)
    echo "Usage: bash web_service.sh [start|stop|restart|status|install-service]"
    ;;
esac
