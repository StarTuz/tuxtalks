import psutil

print("🔍 Searching for Elite Dangerous via cmdline...")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmd = proc.info['cmdline']
        if cmd:
            cmd_str = " ".join(cmd)
            if "Elite" in cmd_str or "359320" in cmd_str:
                print(f"✅ Found candidate: {proc.info['name']} (PID: {proc.info['pid']})")
                print(f"   Cmd: {cmd_str[:200]}...") # Truncate for readability
    except:
        pass
