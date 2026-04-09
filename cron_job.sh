#!/bin/bash
export PATH=$PATH:/usr/local/bin
cd ~/prediction-tracker
python3 update_site.py
if [ -d .git ]; then
  git add data.json
  git commit -m "Daily research update: $(date +'%Y-%m-%d')"
  git push origin main
fi
