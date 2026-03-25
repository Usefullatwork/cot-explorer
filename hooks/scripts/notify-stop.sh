#!/usr/bin/env bash
# notify-stop.sh — Send OS notification when Claude finishes a response
# Hook event: Stop
# Supports Windows (PowerShell toast), macOS (osascript), Linux (notify-send)

TITLE="Claude Code"
MSG="Task complete — ready for review"

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    # Windows: PowerShell balloon notification (non-blocking)
    powershell.exe -NoProfile -Command "
      Add-Type -AssemblyName System.Windows.Forms
      \$n = New-Object System.Windows.Forms.NotifyIcon
      \$n.Icon = [System.Drawing.SystemIcons]::Information
      \$n.Visible = \$true
      \$n.ShowBalloonTip(5000, '$TITLE', '$MSG', 'Info')
      Start-Sleep -Seconds 6
      \$n.Dispose()
    " &
    ;;
  Darwin*)
    # macOS: native notification center
    osascript -e "display notification \"$MSG\" with title \"$TITLE\"" &
    ;;
  Linux*)
    # Linux: freedesktop notification
    notify-send "$TITLE" "$MSG" 2>/dev/null || true
    ;;
esac

exit 0
