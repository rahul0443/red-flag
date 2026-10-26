"""CPU-only: copy Muse Glimmer 30B weights (Apache-2.0) into a Modal volume. Run: modal run training/modal_download.py"""
import modal

app = modal.App("redflag-glimmer-download")
vol = modal.Volume.from_name("redflag-glimmer-vol", create_if_missing=True)
image = (modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub", "hf_transfer")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"}))


@app.function(image=image, volumes={"/vol": vol}, timeout=3600)
def download():
    from huggingface_hub import snapshot_download
    snapshot_download("meta-models/Muse-Glimmer-30B", local_dir="/vol/glimmer")
    vol.commit()
    print("done")
