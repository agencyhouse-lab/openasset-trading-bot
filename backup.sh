#!/bin/bash
# OpenAsset Backup — captures bot code + databases + logs as a timestamped tarball.
# Usage:  bash backup.sh
# Restore:
#   tar xzf /root/openasset_backups/openasset_<timestamp>.tar.gz -C /tmp/restore
#   then manually copy needed files back to /root/openasset_club/telegram_bot/

set -e
DT=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/openasset_backups"
NAME="openasset_${DT}"
STAGE="$BACKUP_DIR/$NAME"

mkdir -p "$STAGE"

echo "═══════════════════════════════════════════════"
echo "  📦 OpenAsset Backup — $DT"
echo "═══════════════════════════════════════════════"

# 1. User bot
echo ""; echo "🔄 1/4: User bot code + databases..."
USER_BOT="/root/openasset_club/telegram_bot"
mkdir -p "$STAGE/user_bot"
cp "$USER_BOT"/*.py "$STAGE/user_bot/" 2>/dev/null || echo "   (no .py files?)"
if [ -d "$USER_BOT/database" ]; then
    cp -r "$USER_BOT/database" "$STAGE/user_bot/"
    echo "   ✅ Databases: $(ls $USER_BOT/database | wc -l) files"
fi
if [ -d "$USER_BOT/logs" ]; then
    cp -r "$USER_BOT/logs" "$STAGE/user_bot/" 2>/dev/null
    echo "   ✅ Logs included"
fi
# Most recent main.py backups too
ls -t "$USER_BOT"/main.py.bak.* 2>/dev/null | head -3 | xargs -I {} cp {} "$STAGE/user_bot/" 2>/dev/null || true
echo "   ✅ User bot files: $(ls $STAGE/user_bot/ 2>/dev/null | wc -l)"

# 2. Admin bot
echo ""; echo "🔄 2/4: Admin bot..."
ADMIN_BOT="/root/openasset_admin_bot"
if [ -d "$ADMIN_BOT" ]; then
    mkdir -p "$STAGE/admin_bot"
    cp "$ADMIN_BOT"/*.py "$STAGE/admin_bot/" 2>/dev/null || true
    echo "   ✅ Admin bot: $(ls $STAGE/admin_bot/ 2>/dev/null | wc -l) files"
else
    echo "   ⏭  Admin bot dir not found — skipped"
fi

# 3. Config (.env etc)
echo ""; echo "🔄 3/4: Config..."
CFG="/root/openasset_club/config"
if [ -d "$CFG" ]; then
    mkdir -p "$STAGE/config"
    cp -r "$CFG"/* "$STAGE/config/" 2>/dev/null || true
    echo "   ✅ Config files: $(ls $STAGE/config/ 2>/dev/null | wc -l)"
fi

# 4. Manifest
cat > "$STAGE/MANIFEST.txt" << MAN
OpenAsset Backup
================
Created: $(date)
Hostname: $(hostname)
Git commit: $(cd /root/openasset-trading-bot 2>/dev/null && git rev-parse --short HEAD 2>/dev/null || echo "unknown")

Contents:
  user_bot/       Python modules + JSON databases + logs
  admin_bot/      Admin bot code
  config/         Environment / config files

Restore notes:
  - JSON databases in user_bot/database/ are the source of truth for
    users, trades, subscriptions, payments, accounts, openasset_accounts.
  - To restore code only:
      tar xzf this_backup.tar.gz
      cp ${NAME}/user_bot/*.py /root/openasset_club/telegram_bot/
      systemctl restart or nohup re-launch the bot
  - To restore data:
      cp ${NAME}/user_bot/database/*.json /root/openasset_club/telegram_bot/database/
MAN

# 5. Compress
echo ""; echo "🔄 4/4: Compressing..."
cd "$BACKUP_DIR"
tar czf "${NAME}.tar.gz" "$NAME"
rm -rf "$NAME"

SIZE=$(du -h "${NAME}.tar.gz" | cut -f1)
echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ Backup complete"
echo "═══════════════════════════════════════════════"
echo "  📦 File:   $BACKUP_DIR/${NAME}.tar.gz"
echo "  📏 Size:   $SIZE"
echo ""
echo "  Recent backups:"
ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -5 | awk '{print "    " $9 " (" $5 ")"}'
echo ""
echo "  To download to your computer:"
echo "    scp root@72.62.254.237:$BACKUP_DIR/${NAME}.tar.gz ."
