import uvicorn
from pyngrok import ngrok
import threading
import time

def run_api():
    uvicorn.run("api:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Запускаем API в отдельном потоке
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Ждем запуска API
    time.sleep(3)
    
    # Создаем ngrok туннель
    public_url = ngrok.connect(8000)
    print(f"API доступен публично: {public_url}")
    print("Обновите API_BASE в index.html на этот URL")
    
    try:
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print("Остановка сервера...")
        ngrok.disconnect(public_url)
