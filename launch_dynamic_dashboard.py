#!/usr/bin/env python3
# BizWiz Dynamic Dashboard Launcher

import subprocess
import sys

def main():
    print("🍗 Launching BizWiz Dynamic Dashboard...")
    print("Features: Real-time data loading, Live API integration")
    print(f"🌐 URL: http://127.0.0.1:8051")
    print(f"📊 Features: Real-time data loading, Live API integration")
    print()
    
    try:
        # Updated path to include BizWiz2.3 subdirectory
        subprocess.run([sys.executable, "BizWiz2.3/dynamic_dashboard.py"])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()