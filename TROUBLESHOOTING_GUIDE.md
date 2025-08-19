# Unified Betting - Troubleshooting Guide

## Quick Fix Tools

### 🚀 **Normal Launch**
- **Use**: `launch.py` or `launch.bat`
- **When**: Everything is working normally
- **What it does**: Starts the full application

### 🔍 **Health Check**
- **Use**: `check_venv.bat` or `launch_menu.bat` → Option 2
- **When**: You suspect issues but aren't sure
- **What it does**: Checks for corrupted packages and missing files, tries to fix minor issues

### 🔧 **Clean Install (Nuclear Option)**
- **Use**: `backend/clean_install.bat` or `launch_menu.bat` → Option 3
- **When**: You see these specific errors:
  - `WARNING: Ignoring invalid distribution ~`
  - `Cannot uninstall selenium None`
  - `The package's contents are unknown`
  - Virtual environment completely broken
- **What it does**: Completely removes and recreates the virtual environment

## Common Issues & Solutions

### ❌ **Backend won't start**
1. Run `check_venv.bat` first
2. If issues found, run `backend/clean_install.bat`
3. Try launching again

### ❌ **Package import errors**
1. Run `check_venv.bat`
2. If corrupted packages found, run `backend/clean_install.bat`
3. Try launching again

### ❌ **Chrome/ChromeDriver issues**
1. Close all Chrome windows manually
2. Run `kill_all.bat` to force cleanup
3. Try launching again

### ❌ **Port already in use**
1. Run `kill_all.bat` to stop all processes
2. Wait 30 seconds
3. Try launching again

## Menu Launcher

Use `launch_menu.bat` for an interactive menu with all options:

```
1. 🚀 Launch Application
2. 🔍 Check Virtual Environment Health  
3. 🔧 Clean Install (Fix Issues)
4. 📦 Setup Dependencies Only
5. 🚪 Exit
```

## Prevention Tips

1. **Don't interrupt installations** - Let them complete
2. **Close Chrome properly** - Don't force-kill it
3. **Use the shutdown script** - `shutdown.bat` to stop properly
4. **Run health checks regularly** - Especially after updates

## When to Use Each Tool

| Tool | When to Use | Frequency |
|------|-------------|-----------|
| `launch.py` | Normal operation | Daily |
| `check_venv.bat` | Suspect issues | Weekly/When problems |
| `clean_install.bat` | Serious corruption | Rare (emergency) |
| `launch_menu.bat` | Want options | Anytime |

## File Locations

- **Main launcher**: `launch.py`
- **Menu launcher**: `launch_with_menu.py`
- **Health check**: `backend/venv_health_check.py`
- **Clean install**: `backend/clean_install.bat`
- **Shutdown**: `shutdown.bat`

## Need Help?

If none of these tools work:
1. Check the logs in `logs/` directory
2. Look for specific error messages
3. Try running health check first
4. Use clean install as last resort 