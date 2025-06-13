
# Installation

```shell
pip install chatterbox-tts
```

# Runpod setup

cd workspace

# Update package lists
apt-get update

# Install Python 3.11
apt install -y python3.11

# Clone Chatterbox repository
git clone <your-repo-url>  # e.g. git clone https://github.com/your-username/chatterbox-tts.git

# Navigate into directory
cd chatterbox-tts

# Create a virtual environment
python3.11 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Run the application
python app.py
