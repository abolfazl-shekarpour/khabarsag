import re

def clean_text(text):
    # Remove all @ symbols
    return re.sub(r'@', '', text)

def add_signature(text, channel):
    # Append the channel name as a signature
    return f"{text}\n\n— {channel}"