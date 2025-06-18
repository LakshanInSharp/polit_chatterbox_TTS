


# Runpod setup

cd workspace

apt-get update

apt install -y python3.11

git clone https://github.com/LakshanInSharp/polit_chatterbox_TTS.git

cd polit_chatterbox_TTS

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

# Run the application
python app.py
