#!/usr/bin/env python3
"""
Unified Chat App Runner
Starts Backend (FastAPI), Frontend (React), and Database all in one command

Usage:
    python run.py              # Starts everything
    python run.py --backend    # Backend only
    python run.py --frontend   # Frontend only
    python run.py --help       # Show options
"""

import os
import sys
import subprocess
import time
import signal
import platform
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_info(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_start(text):
    print(f"{Colors.BLUE}→{Colors.END} {text}")

def get_root_dir():
    """Get the root directory of the project"""
    return Path(__file__).parent.absolute()

def check_python_packages():
    """Check if required Python packages are installed"""
    print_start("Checking Python packages...")
    
    required = ['fastapi', 'uvicorn']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print_info(f"Found {package}")
        except ImportError:
            missing.append(package)
            print_warning(f"Missing {package}")
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print_start(f"Installing with: pip install {' '.join(missing)}")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, check=True)
        print_info("Packages installed")

def check_node_packages():
    """Check if Node packages are installed"""
    print_start("Checking Node packages...")
    
    root = get_root_dir()
    frontend_dir = root / 'frontend'
    
    node_modules = frontend_dir / 'node_modules'
    
    if not node_modules.exists():
        print_warning("Node modules not found, running npm install...")
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        print_info("Node packages installed")
    else:
        print_info("Node packages found")

def start_backend(port=8000):
    """Start FastAPI backend server"""
    print_start(f"Starting Backend on http://localhost:{port}...")
    
    root = get_root_dir()
    backend_dir = root / 'backend'
    
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    cmd = [
        sys.executable,
        '-m',
        'uvicorn',
        'app.main:app',
        '--reload',
        '--host', '0.0.0.0',
        '--port', str(port)
    ]
    
    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    print_info(f"Backend process started (PID: {process.pid})")
    return process

def start_frontend(port=3000):
    """Start React frontend dev server"""
    print_start(f"Starting Frontend on http://localhost:{port}...")
    
    root = get_root_dir()
    frontend_dir = root / 'frontend'
    
    env = os.environ.copy()
    env['REACT_APP_API_URL'] = 'http://localhost:8000'
    env['PORT'] = str(port)
    
    cmd = ['npm', 'start']
    
    process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    print_info(f"Frontend process started (PID: {process.pid})")
    return process

def wait_for_service(url, timeout=30):
    """Wait for a service to be ready"""
    import urllib.request
    import urllib.error
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except (urllib.error.URLError, Exception):
            time.sleep(1)
    
    return False

def main():
    """Main entry point"""
    print_header("🚀 Chat App - Unified Launcher")
    
    root = get_root_dir()
    
    # Parse arguments
    backend_only = '--backend' in sys.argv
    frontend_only = '--frontend' in sys.argv
    help_flag = '--help' in sys.argv or '-h' in sys.argv
    
    if help_flag:
        print("""
Usage:
    python run.py              # Start everything (Backend + Frontend)
    python run.py --backend    # Start backend only
    python run.py --frontend   # Start frontend only
    python run.py --help       # Show this help

Ports:
    Backend:  http://localhost:8000
    Frontend: http://localhost:3000
    
Access:
    Browser: http://localhost:3000
    API:     http://localhost:8000
    Health:  http://localhost:8000/health

To stop: Press Ctrl+C (Cmd+C on Mac)
        """)
        return
    
    # Start services
    processes = []
    
    try:
        if not frontend_only:
            print_info("Preparing backend...")
            check_python_packages()
            backend_process = start_backend()
            processes.append(backend_process)
            
            # Wait for backend to be ready
            print_start("Waiting for backend to be ready...")
            if wait_for_service('http://localhost:8000/health'):
                print_info("Backend is ready! ✓")
            else:
                print_warning("Backend startup delayed, continuing anyway...")
        
        time.sleep(1)
        
        if not backend_only:
            print_info("Preparing frontend...")
            check_node_packages()
            frontend_process = start_frontend()
            processes.append(frontend_process)
            
            # Wait for frontend to be ready
            print_start("Waiting for frontend to be ready...")
            if wait_for_service('http://localhost:3000'):
                print_info("Frontend is ready! ✓")
            else:
                print_warning("Frontend startup delayed, continuing anyway...")
        
        # Display ready message
        print_header("✅ All Services Running!")
        print(f"{Colors.GREEN}Backend (API):  {Colors.END}http://localhost:8000")
        print(f"{Colors.GREEN}Frontend (Web): {Colors.END}http://localhost:3000")
        print(f"{Colors.GREEN}Health Check:   {Colors.END}http://localhost:8000/health")
        print(f"\n{Colors.YELLOW}Press Ctrl+C to stop all services{Colors.END}\n")
        
        # Display test commands
        print_header("Quick Test Commands")
        print(f"""
# Test backend health
curl http://localhost:8000/health

# Test sync endpoint
curl -X POST http://localhost:8000/api/offline/messages/sync \\
  -H "Content-Type: application/json" \\
  -d '{{"messages":[],"device_id":"test"}}'

# Watch logs (in new terminal)
cd backend && tail -f logs.txt  (if you enable logging)
        """)
        
        # Keep processes running
        for process in processes:
            process.wait()
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Shutting down services...{Colors.END}")
        
        # Terminate all processes
        for i, process in enumerate(processes, 1):
            try:
                process.terminate()
                print_warning(f"Stopped process {i}")
            except:
                pass
        
        # Give them time to gracefully shut down
        time.sleep(1)
        
        # Force kill if needed
        for process in processes:
            try:
                if process.poll() is None:
                    process.kill()
            except:
                pass
        
        print_info("All services stopped")
        sys.exit(0)
    
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
