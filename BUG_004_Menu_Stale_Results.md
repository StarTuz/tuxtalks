# BUG #004: Runtime Menu Shows Stale Results

**Date:** 2025-12-12  
**Bug ID:** #004  
**Severity:** Medium  
**Status:** ✅ **VERIFIED** - Working correctly

## Issue Description

When issuing multiple search commands in quick succession, the `tuxtalks-menu` GUI displays results from the **previous** search instead of updating with the new results.

## Steps to Reproduce

1. Start `tuxtalks-menu`
2. Run `tuxtalks` (CLI)
3. Say "play beethoven" → Menu displays Beethoven results
4. Click "Select" → Music plays, menu clears
5. Say "play gustav holst" → **BUG: Menu still shows Beethoven results**

## Expected Behavior

- Menu should update with new Gustav Holst results (9 items)
- Title should change to "Select Artist (Page 1)"
- Listbox should show Holst artists/albums/playlists

## Actual Behavior

- Menu continues to show old Beethoven results
- No visual update when new request arrives
- Console log shows: `[Selection] Sending to GUI menu: 9 items`
- Console log shows: `[IPC Client] Waiting for selection (timeout: 60s)...`

## Debug Information

**Console Log:**
```
DEBUG: Music command (not gaming), trying Ollama with keyword fallback: 'play gustav holst'
DEBUG: Added library context: 50 artists
DEBUG: Querying Ollama: 'play gustav holst'
DEBUG: Ollama success: play_artist (conf: 0.95)
INFO: Ollama: play_artist (confidence: 0.95)
🗣 Queued to speak: Searching for gustav holst
[Selection] Sending to GUI menu: 9 items
[IPC Client] Waiting for selection (timeout: 60s)...
```

**GUI State:**
- Window title: "Select Option (Page 1)"
- Listbox shows: Beethoven results (1. Artist: Beethoven, 2. Composer: Beethoven, etc.)
- Should show: Gustav Holst results

## Root Cause Analysis

### Hypothesis 1: Race Condition in selection_ready Event

**Code Flow:**
```python
# runtime_menu.py line 146
def _handle_selection_request(self, title, items, page):
    self.request_queue.put(('request', title, items, page))  # Queue request
    self.selection_ready.wait()  # ⚠️ BLOCKS until user selects
    self.selection_ready.clear()
    return (self.selected_index, self.cancelled)
```

**Problem:**
- Each IPC request runs in its **own thread**
- When request #1 arrives, it queues and waits on `selection_ready`
- When request #2 arrives **before user selects**, it also queues and waits
- **Both threads** are waiting on the **same event**
- When event is set, **both threads wake up** → race condition

### Hypothesis 2: Queue Not Being Processed

The `_process_queue()` method runs every 100ms, but:
- It only processes **available** queue items
- If IPC thread is blocking on `selection_ready.wait()`, the queue item might not be dequeued properly

### Hypothesis 3: Display Not Updating

The `_display_selection()` method should:
```python
# Line 177 - Should clear old items
self.listbox.delete(0, tk.END)
for i, item in enumerate(items, 1):
    self.listbox.insert(tk.END, f"{i}. {item}")
```

But if this isn't being called for the new request, the old display persists.

## Proposed Fix

### Option 1: Single Request at a Time (Recommended)

Prevent multiple concurrent requests by:
- Cancelling previous request when new one arrives
- Only allowing one active selection at a time

```python
def _handle_selection_request(self, title, items, page):
    # Cancel any pending selection
    if self.selection_ready.is_set():
        self.selection_ready.clear()
    
    # Queue new request (this will overwrite display)
    self.request_queue.put(('request', title, items, page))
    
    # Wait for user selection
    self.selection_ready.wait()
    self.selection_ready.clear()
    
    return (self.selected_index, self.cancelled)
```

### Option 2: Request ID Tracking

Add unique IDs to each request to prevent race conditions:

```python
self.request_id = 0
self.current_request_id = None

def _handle_selection_request(self, title, items, page):
    req_id = self.request_id
    self.request_id += 1
    
    self.request_queue.put(('request', req_id, title, items, page))
    
    # Wait for this specific request to complete
    while self.current_request_id != req_id or not self.selection_ready.is_set():
        time.sleep(0.1)
    
    return (self.selected_index, self.cancelled)
```

## Debug Steps

1. **Add logging** to see if `_display_selection()` is being called:
   ```python
   print(f"[Runtime Menu] Displaying: {title}, {len(items)} items, queue size: {self.request_queue.qsize()}")
   ```

2. **Check thread count** - are multiple IPC threads accumulating?

3. **Log selection_ready events** - when is it being set/cleared?

## Impact

- **Severity:** Medium (workaround: restart menu between searches)
- **Frequency:** Every time user makes back-to-back searches
- **User Experience:** Confusing - displays wrong results

## Workaround

**Current:** Restart `tuxtalks-menu` between searches
```bash
pkill -f tuxtalks-menu
tuxtalks-menu &
```

---

**Reported by:** startux  
**Fixed by:** Antigravity  
**Date Fixed:** 2025-12-12

## ✅ Root Cause Confirmed

After adding debug logging, the root cause was **definitively identified**:

**Problem:** The IPC server (`ipc_server.py`) is **single-threaded** and can only handle **one client connection at a time**.

**Sequence:**
1. First request (Beethoven) arrives → Server accepts connection → Blocks waiting for user selection
2. Second request (Holst) arrives → **Server cannot accept** because it's still handling first connection
3. First request times out (60s) → Server finally accepts second connection
4. But by then, user has already seen timeout and moved on

**Evidence from logs:**
```
# First request - Full debug output
[Runtime Menu] 📨 IPC request received: 'Select Option', 10 items, page 1
[Runtime Menu] 🔄 Processing queued request...
[Runtime Menu] ✅ Display complete

# Second request - NO menu logs at all!
[Selection] Sending to GUI menu: 9 items
[IPC Client] Waiting for selection (timeout: 60s)...
[IPC Client] ⏱  Selection timed out
```

The menu **never received** the second request because the server was blocked.

## ✅ Fix Implemented

**Two-part solution:**

### Part 1: Multi-threaded IPC Server

**File:** `ipc_server.py` (lines 91-100)

**Change:** Handle each client in a separate thread

```python
# Before (single-threaded):
client_socket, _ = self.server_socket.accept()
self._handle_client(client_socket)  # Blocks server

# After (multi-threaded):
client_socket, _ = self.server_socket.accept()
client_thread = threading.Thread(
    target=self._handle_client,
    args=(client_socket,),
    daemon=True
)
client_thread.start()  # Non-blocking!
print(f"[IPC Server] 🧵 Started client thread {client_thread.name}")
```

**Result:** Server can now accept multiple connections concurrently.

### Part 2: Request ID Tracking \u0026 Cancellation

**File:** `runtime_menu.py` (lines 42-46, 144-180, 199-212)

**Changes:**
1. Added request ID tracking:
   ```python
   self.request_id = 0  # Increments with each request
   self.active_request_id = None  # Currently displayed request
   self.request_lock = threading.Lock()  # Thread-safe access
   ```

2. Automatic cancellation of old requests:
   ```python
   # In _handle_selection_request():
   my_request_id = self.request_id
   self.request_id += 1
   
   # Cancel previous pending request
   if self.active_request_id is not None and self.active_request_id != my_request_id:
       print(f"[Runtime Menu] ❌ Cancelling previous request #{self.active_request_id}")
       self.cancelled = True
       self.selection_ready.set()  # Wake up old thread
   ```

3. Set active request when displaying:
   ```python
   # In _display_selection():
   with self.request_lock:
       self.active_request_id = req_id  # This request is now active
   ```

4. Check if superseded before returning:
   ```python
   # Before returning selection:
   with self.request_lock:
       if self.active_request_id != my_request_id:
           print(f"[Runtime Menu] 🚫 Request #{my_request_id} was superseded")
           return (-1, True)  # Cancelled
   ```

**Result:** New requests automatically cancel old ones, ensuring the GUI always shows the latest results.

## Expected Behavior After Fix

**Old behavior:**
```
Search 1: "beethoven" → Menu shows Beethoven → Times out
Search 2: "holst" → Menu still shows Beethoven (stuck!) → Times out
```

**New behavior:**
```
Search 1: "beethoven" → Menu shows Beethoven
Search 2: "holst" → Menu IMMEDIATELY updates to Holst, Beethoven request cancelled
```

**Console output:**
```
[Runtime Menu] 📨 IPC request #0 received: 'Select Option', 10 items (Beethoven)
[Runtime Menu] 🔄 Processing queued request #0
[Runtime Menu] ✅ Display complete
[Runtime Menu] ⏳ Waiting for user selection (request #0)...

[Runtime Menu] 📨 IPC request #1 received: 'Select Option', 9 items (Holst)
[Runtime Menu] ❌ Cancelling previous request #0
[Runtime Menu] 🔄 Processing queued request #1
[Runtime Menu] 🗑️  Cleared 10 old items (Beethoven)
[Runtime Menu] ➕ Added 9 new items (Holst)
[Runtime Menu] ✅ Display complete

[Runtime Menu] 🚫 Request #0 was superseded by #1  ← Old thread gets cancelled
[Runtime Menu] ⏳ Waiting for user selection (request #1)...
```

## Testing Instructions

1. **Restart menu** to pick up the fix:
   ```bash
   pkill -f tuxtalks-menu && tuxtalks-menu &
   ```

2. **Test rapid searches:**
   ```
   Say: "mango play beethoven"
   → Menu shows Beethoven results
   
   Immediately say: "mango play holst"
   → Menu should INSTANTLY update to Holst results
   
   Click "Select" on a Holst item
   → Should play Holst (not Beethoven)
   ```

3. **Check debug logs** - You should see:
   - `🧵 Started client thread` for each request
   - `❌ Cancelling previous request` when new search arrives
   - `🗑️ Cleared X old items` followed by `➕ Added Y new items`

## Files Modified

- `ipc_server.py` - Multi-threaded client handling
- `runtime_menu.py` - Request ID tracking and cancellation logic

## Impact

- ✅ Menu now updates immediately with new results
- ✅ No more stale data displayed
- ✅ Concurrent requests handled gracefully
- ✅ Backward compatible (no API changes)

**Status:** Ready for testing!
