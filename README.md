# AI-Chatbot-with-Sentiment-Analysis-using-Python


## 1) Open a terminal

Use **PowerShell** (recommended) or **Command Prompt**.

To open PowerShell: Start → type **PowerShell** → Enter.

Change to your project folder:

```powershell
cd "C:\Users\<YourName>\Desktop\chatbot"
```

---

## 2) (Recommended) Create & activate a Python virtual environment

This keeps packages tidy.

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run (one-time) to allow scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

You should now see `(venv)` at the prompt.

---

## 3) Install Python dependencies

If you created `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Or install directly:

```powershell
pip install ollama transformers torch psutil requests
```

**Notes / Troubleshooting**

* If `pip install torch` fails because it needs a specific CUDA wheel, install the CPU wheel first or follow PyTorch instructions for your CUDA version. For many users CPU-only `pip install torch` works fine.
* If you get errors about C++ build tools, install *Microsoft Visual C++ Build Tools* (link from Microsoft) and rerun pip.
* `tkinter` is included with standard Python on Windows. If GUI fails, reinstall Python using the official installer and enable Tcl/Tk.

---

## 4) Install Ollama (local LLM engine)

1. Download & install from: [https://ollama.ai/download](https://ollama.ai/download)
   (choose Windows installer and run it).

2. After install, verify in the same terminal:

```powershell
ollama --version
ollama list
```

`ollama list` may show nothing yet (no models) — that’s fine.

---

## 5) Pull the model(s)

Recommended: pull the main model **mistral** (Ollama alias) — easiest and usually available.

```powershell
ollama pull mistral
```

If you specifically want a tagged quantized model and Ollama supports it on your build, try:

```powershell
ollama pull mistral:7b-instruct-q5_0
```

If you see `Error: pull model manifest: file does not exist`, use plain `ollama pull mistral` (the registry name can vary by Ollama version).

Also pull a small fallback (optional):

```powershell
ollama pull llama3
```

Confirm:

```powershell
ollama list
```

You should see entries (e.g. `mistral`, `llama3`) with sizes.

---

## 6) (Optional) Check GPU availability & free memory

To see if you have an NVIDIA GPU and VRAM available:

```powershell
nvidia-smi
```

If `nvidia-smi` is not found, you may not have NVIDIA drivers or a discrete NVIDIA GPU — the models will run on CPU.

**If VRAM is small (e.g. 4 GB or less)** prefer CPU mode or a smaller model.

---

## 7) Run the chatbot

In the activated virtualenv and correct folder:

**Normal run** (let Ollama decide GPU/CPU):

```powershell
python emotion_chatbot_final.py
```

**Force CPU mode** (if you got CUDA OOM earlier):

* CMD:

```cmd
set OLLAMA_NO_GPU=1
python emotion_chatbot_final.py
```

* PowerShell (single session):

```powershell
$env:OLLAMA_NO_GPU = "1"
python emotion_chatbot_final.py
```

(That environment variable tells Ollama to not use GPU.)

---

## 8) Quick interactive checks

If you want to sanity-check the model outside the GUI:

Run an interactive shell with the model:

```powershell
ollama run mistral
```

Type `Hello` and confirm the model replies.

To remove models later:

```powershell
ollama rm mistral
ollama rm llama3
```

---

## 9) Common errors & fixes

**A. `cudaMalloc failed: out of memory` / `CUDA error 500`**

* Free GPU memory (close Chrome, editors with GPU kernels).
* Use a smaller model or force CPU: `$env:OLLAMA_NO_GPU="1"` then run Python.
* Pull a smaller model (e.g. `ollama pull llama3`).

**B. `Error: pull model manifest: file does not exist`**

* Model tag not listed. Use `ollama pull mistral` (no tag) or check `ollama` docs/library for available names.

**C. `ModuleNotFoundError: psutil` or similar**

* Activate virtualenv then `pip install psutil` (or rerun requirements install).

**D. `PermissionError` when running Ollama**

* Run terminal as Administrator. Or check that Ollama service is running.

**E. Transformer deprecation warnings**

* Safe to ignore. If you want quiet console, add `import warnings; warnings.filterwarnings("ignore")` at top of script.

---

## 10) Helpful debugging commands

* Show installed Python packages:

```powershell
pip list
```

* Check Python path used by `python`:

```powershell
python -c "import sys; print(sys.executable)"
```

* Show Ollama models:

```powershell
ollama list
```

* Test model in terminal:

```powershell
ollama run mistral
```

---

## 11) Example test sentences to try in the GUI

* `I’m nervous but excited about tomorrow’s interview.`
* `I just finished a big project — I feel so proud!`
* `My teacher scolded me yesterday and I’m upset.`
* `I’m thinking about having tea while sitting in the garden.`

You should see multi-emotion outputs and empathetic bot replies.

---

## 12) If you want a one-click start (Windows .bat)

Create `run_chatbot.bat` in your project folder with:

```bat
@echo off
cd /d %~dp0
call venv\Scripts\activate
python emotion_chatbot_final.py
pause
```

Double-click to launch the virtualenv and run the bot.

---

## Final tips

* If you have a GPU and want speed, install the appropriate CUDA-enabled PyTorch wheel for your CUDA driver (from PyTorch website) — this speeds up emotion inference. Ollama handles LLM GPU use.
* Keep models you need and `ollama rm` the rest to free disk space.
* If anything fails, copy the exact error text and paste it here — I’ll diagnose the precise fix.

