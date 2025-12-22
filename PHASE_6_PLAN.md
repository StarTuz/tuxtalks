# Phase 6: Fix Display Name Bugs - Implementation Plan

**Date:** December 13, 2025 (09:33 PST)  
**Status:** 🔧 In Progress  
**Target:** Fix all display/refresh bugs

---

## 🔍 Root Cause Identified

### **The Problem:**

**TWO different methods build `profile_display_map` with DIFFERENT logic:**

**Method 1: `refresh_profile_list()` (lines 1546-1560):**
```python
for p in group_p_objs:
    d_name = p.name
    # Complex logic with multiple checks
    if "(" in p.name and p.name.endswith(")"):
        if p.name.startswith(p.group):
            remainder = p.name[len(p.group):].strip()
            if remainder.startswith("(") and remainder.endswith(")"):
                d_name = remainder[1:-1]
    self.profile_display_map[d_name] = p.name
```

**Method 2: `on_game_select()` (lines 1586-1595):**
```python
for p in group_p_objs:
    d_name = p.name
    # Simpler logic, missing checks
    if p.name.startswith(p.group):
        remainder = p.name[len(p.group):].strip()
        if remainder.startswith("(") and remainder.endswith(")"):
            d_name = remainder[1:-1]
    self.profile_display_map[d_name] = p.name
```

**Difference:** Method 1 checks `if "(" in p.name`, Method 2 doesn't!

**Result:** Inconsistent display names depending on which path rebuilds the map!

---

## 🎯 The Fix

### **Solution: Centralize display name logic**

**Create ONE method that both use:**

```python
def _build_display_name(self, profile):
    """Convert full profile name to display name.
    
    Example:
      "X4 Foundations (GOG) (inputmap.xml)" → "inputmap.xml"
    """
    d_name = profile.name
    
    # Only strip if name follows pattern: "Group (variant)"
    if profile.group and profile.name.startswith(profile.group):
        remainder = profile.name[len(profile.group):].strip()
        if remainder.startswith("(") and remainder.endswith(")"):
            d_name = remainder[1:-1]
    
    return d_name
```

**Then use it everywhere:**
```python
# In refresh_profile_list():
for p in group_p_objs:
    d_name = self._build_display_name(p)  # ← Consistent!
    self.profile_display_map[d_name] = p.name

# In on_game_select():
for p in group_p_objs:
    d_name = self._build_display_name(p)  # ← Consistent!
    self.profile_display_map[d_name] = p.name
```

---

## 📋 Implementation Steps

### **Step 1: Create centralized method** ✅
- Add `_build_display_name(profile)` method
- Use consistent, tested logic
- Document expected behavior

### **Step 2: Update refresh_profile_list()** ✅
- Replace inline logic with method call
- Clear `profile_display_map` at start (important!)
- Add validation

### **Step 3: Update on_game_select()** ✅
- Replace inline logic with method call
- Ensure same behavior as refresh

### **Step 4: Add safeguards** ✅
- Clear map before rebuilding (prevent stale data)
- Validate dropdown values against map
- Add error handling for missing profiles

### **Step 5: Fix game dropdown** ✅
- Ensure all groups appear
- Fix any filtering issues

---

## 🔧 Additional Improvements

### **Clear stale data:**
```python
# At start of refresh_profile_list():
self.profile_display_map = {}  # ← Clear stale mappings!
self.profile_display_map.clear()
```

### **Validate before use:**
```python
# In get_active_profile():
if selected_name in self.profile_display_map:
    real_name = self.profile_display_map[selected_name]
else:
    # Fallback: assume it's already the real name
    real_name = selected_name
```

---

## ✅ Expected Results

### **After fixes:**

**BUG #1** ❌ (Already fixed - removed Add Bind)
**BUG #2** ❌ (Already fixed - removed Remove Bind)
**BUG #3** ✅ **WILL BE FIXED:**
- Display names consistent
- No UI corruption
- All games appear in dropdown

**Game dropdown issue** ✅ **WILL BE FIXED:**
- All configured games appear
- Proper filtering
- Consistent display

---

## 🎯 Ready to implement!

**Starting now...**
