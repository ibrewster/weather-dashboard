#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MTU5Zjk0YTA2YTU0NmJjYmIyNGM5NGE4MjExODY1MyIsImlhdCI6MTc2MTY4NzcxNSwiZXhwIjoyMDc3MDQ3NzE1fQ.LavjahxRcnTuvnbYeRjQkDPNdY0QnT2GaRS_xWytI2k"
URL="http://10.27.81.207:8123/dashboard-environment/0?kiosk="
IMG_PATH="/tmp/dashboard.png"

curl -s -H "Authorization: Bearer $TOKEN" "$URL" > /tmp/dashboard.html
#wkhtmltoimage --width 800 --height 600 /tmp/dashboard.html "$IMG_PATH"
