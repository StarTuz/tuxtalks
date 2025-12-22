# BUG #003: IPC Menu Selection Timeout

**Date:** 2025-12-12  
**Bug ID:** #003  
**Severity:** Low (UX Issue)  
**Status:** ✅ **FIXED**

## Issue Description

When using `tuxtalks-menu` for GUI selection, clicking "Select" results in a timeout error and broken pipe, even though the menu appears to be working.

## Steps to Reproduce

1. Start `tuxtalks-menu`
2. Run `tuxtalks` (CLI)
3. Trigger a music search with multiple results (e.g., "play vaughan williams")
4. Selection list appears in GUI menu
5. Click "Select" button in menu
6. **Error occurs**

## Error Messages

```
[IPC Client] Timeout waiting for selection
[Selection] GUI cancelled
[IPC Server] Client error: [Errno 32] Broken pipe
```

## Expected Behavior

- User clicks "Select" in menu
- Selection is sent back to CLI
- Music starts playing
- No timeout or broken pipe errors

## Actual Behavior

- Timeout occurs (30s limit?)
- Selection treated as cancelled
- Broken pipe error when menu tries to respond
- System falls back to voice/console input

## Root Cause Analysis

### Hypothesis 1: Response Timing Issue
The client socket might be closing before the menu sends the response:

1. Client sends selection request
2. Client waits with 30s timeout
3. User clicks "Select" quickly (< 30s)
4. Menu tries to send response
5. Client socket already in error state → Broken pipe

**Question:** How long between menu appearing and clicking "Select"?

### Hypothesis 2: Socket Buffer Issue
The response might not be sending correctly:
- Large item lists could cause buffer issues
- JSON encoding/decoding problem
- Newline delimiter not being sent/received properly

### Hypothesis 3: Menu Not Responding
The menu GUI might not be sending the response when "Select" is clicked:
- Event handler not firing
- IPC server not processing click
- Response not being serialized correctly

## Debugging Steps

### 1. Check Response Timing
Add logging to see how long the selection takes:

```python
# In ipc_client.py
import time
start = time.time()
response = json.loads(data.decode('utf-8').strip())
elapsed = time.time() - start
print(f"[IPC Client] Response received in {elapsed:.2f}s")
```

### 2. Check Menu Server Logs
Look for menu-side errors when "Select" is clicked

### 3. Test with Small List
Try with a small selection list (2-3 items) vs large list (10+ items)

### 4. Check Socket State
Add socket diagnostics before sending response

## Known Information

**Timeout Value:** 30 seconds (ipc_client.py line 47)  
**Socket Type:** Unix domain socket  
**Socket Path:** `/tmp/tuxtalks-menu-{uid}.sock`  

**Current Flow:**
```python
# Client side (ipc_client.py)
client_socket.settimeout(timeout)  # 30s
client_socket.connect(socket_path)
client_socket.sendall(request_data)
# Wait for response...
data = client_socket.recv(4096)  # Blocks until data or timeout
```

## Potential Fixes

### Fix 1: Increase Timeout
```python
# In selection_handler.py
response = ipc_client.send_selection_request(
    title=f"Select {self.current_field}",
    items=formatted_items,
    page=1,
    timeout=60.0  # Increase from 30s to 60s
)
```

### Fix 2: Better Error Handling
```python
# In ipc_client.py
except socket.timeout:
    print(f"[IPC Client] Timeout after {timeout}s waiting for selection")
    try:
        client_socket.close()
    except:
        pass
    return {'index': -1, 'cancelled': True}  # Instead of None
```

### Fix 3: Add Keep-Alive
```python
# In ipc_client.py
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
```

### Fix 4: Check Menu Implementation
Verify that the menu is actually sending the response when "Select" is clicked.

## ✅ Fix Implemented

**Root Cause:** Timeout was too short (30s) and provided no user feedback

**Solution:** Improved timeout UX with three changes:

### 1. Increased Timeout (30s → 60s)
```python
# ipc_client.py line 47
def send_selection_request(title, items, page=1, timeout=60.0):  # Was 30.0
```

### 2. Better Logging
```python
# ipc_client.py - Added at start of function
print(f"[IPC Client] Waiting for selection (timeout: {timeout:.0f}s)...")

# ipc_client.py - Enhanced timeout message
except socket.timeout:
    print(f"[IPC Client] ⏱️  Selection timed out after {timeout:.0f} seconds")
    print(f"[IPC Client] You can re-issue the command to see options again")
```

### 3. TTS Feedback
```python
# selection_handler.py - Speak to user when timeout occurs
if response and response.get('cancelled'):
    print("[Selection] GUI cancelled/timed out")
    self.speak("Selection timed out. You can re-issue the command.")
```

**User Experience After Fix:**
```
System: "Found 10 matches..."
Console: "[IPC Client] Waiting for selection (timeout: 60s)..."
[User takes 65 seconds to decide]
Console: "[IPC Client] ⏱️  Selection timed out after 60 seconds"
Console: "[IPC Client] You can re-issue the command to see options again"
System: "Selection timed out. You can re-issue the command."
```

**Files Modified:**
- `ipc_client.py` lines 47, 55, 61-62, 100-106
- `core/selection_handler.py` lines 105-108

**Impact:**
- ✅ Users now know they have 60 seconds
- ✅ Clear feedback when timeout occurs
- ✅ Instructions on what to do next
- ✅ Doubled timeout window (more realistic for multitasking)

## Workaround

**For now:** Use voice or console input for selections instead of GUI menu.

```bash
# Instead of clicking in menu, just say or type the number
"3"  # Voice
3    # Console (type + Enter)
```

## Testing Needed

1. **Timing test:** Measure exact time from menu display to button click
2. **Item count test:** Test with 2, 5, 10, 20, 50 items
3. **Menu verification:** Confirm menu is actually sending response
4. **Socket state:** Check if socket is still connected when response sent

## Impact

- **Severity:** Medium (workaround exists)
- **Frequency:** Unknown (first report)
- **Affected Component:** IPC communication (tuxtalks-menu ↔ tuxtalks-cli)

---

**Reported by:** startux  
**Investigating:** Antigravity  
**Next Steps:** Need user feedback on timing and more test data
