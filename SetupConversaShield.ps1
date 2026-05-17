# SetupConversaShield.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "ConversaShield public hackathon dependencies installed." -ForegroundColor Green
Write-Host "Install Ollama separately and pull the Gemma model." -ForegroundColor Yellow