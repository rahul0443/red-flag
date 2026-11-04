"""Public deployment of Red Flag on Modal (CPU only). Deploy with: modal deploy deploy/modal_web.py
API keys come from the Modal secret 'redflag-keys' (MODEL_API_KEY, BASETEN_API_KEY), never from the repo."""
import modal

image = (modal.Image.debian_slim(python_version="3.12")
         .pip_install("openai", "python-dotenv", "httpx", "fastapi", "uvicorn", "python-multipart", "modal")
         .env({"DAILY_CAP": "600", "PER_IP_PER_MIN": "10", "MAX_CONCURRENT": "6"})
         .add_local_python_source("redflag")
         .add_local_dir("web", "/root/web"))

app = modal.App("redflag-web", image=image)


@app.function(secrets=[modal.Secret.from_name("redflag-keys")], min_containers=1, scaledown_window=900, timeout=300)
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def web():
    from redflag.api.server import app as fastapi_app
    return fastapi_app
