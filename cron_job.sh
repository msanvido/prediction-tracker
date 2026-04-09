#!/bin/bash
# Prediction Tracker Daily Update Script
export PATH=$PATH:/usr/local/bin

# Navigate to project directory
cd ~/prediction-tracker

# Run the update script
python3 update_site.py

# Optional: Push to GitHub if credentials exist
# if [ -f ~/.git-credentials ]; then
#   git add data.json
#   git commit -m "Daily research update: $(date +'%Y-%m-%d')"
#   git push origin main
# fi
