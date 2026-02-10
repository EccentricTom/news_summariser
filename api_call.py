import requests
from src.news_summariser.config import load_settings

def main():
    settings = load_settings()
    print(settings)
    response = requests.get(f"{settings.api_url}/news?lang={settings.api_lang}")
    response.raise_for_status()
    print(response.json().keys())



if __name__ == "__main__":
    main()