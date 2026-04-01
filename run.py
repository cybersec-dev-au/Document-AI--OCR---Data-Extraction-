import subprocess
import webbrowser
import time
import os
import sys

def cleanup_port(port):
    """
    Kills any process running on the specified port.
    """
    if os.name == 'nt':  # Windows
        try:
            # Find PID using netstat
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            for line in output.splitlines():
                if "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    print(f"🧹 Killing existing process on port {port} (PID: {pid})...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        except subprocess.CalledProcessError:
            # No process found on that port
            pass

def main():
    print("🚀 Starting DocuScan AI...")
    
    # 1. Ensure port 8000 is free
    cleanup_port(8000)
    
    # 1. Install dependencies if needed (optional, for convenience)
    # subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 2. Get absolute path of backend
    backend_path = os.path.join(os.getcwd(), "backend", "main.py")
    
    # 3. Start Backend as a separate process
    print("📡 Launching Backend (FastAPI)...")
    backend_proc = subprocess.Popen([sys.executable, backend_path])
    
    # 4. Wait for backend to warm up (Models can be slow to load)
    print("⏳ Warming up AI models (PaddleOCR)... This might take 10-30 seconds on first run.")
    time.sleep(5)
    
    # 5. Open Frontend
    from pathlib import Path
    frontend_path = os.path.join(os.getcwd(), "frontend", "index.html")
    frontend_uri = Path(frontend_path).as_uri()
    print(f"🎨 Opening Frontend: {frontend_uri}")
    webbrowser.open(frontend_uri)
    
    print("\n✅ System Running!")
    print("----------------------------------------")
    print("Press Ctrl+C to stop the backend.")
    print("----------------------------------------")
    
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
        backend_proc.terminate()

if __name__ == "__main__":
    main()
