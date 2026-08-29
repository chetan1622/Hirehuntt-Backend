# Modern UI & Gamification Update

Is plan ka maksad app ko bilkul naya, fast aur attractive look dena hai, aur user engagement badhane ke liye naye features add karna hai.

## Proposed Changes

### 1. Dark Mode Fix
- **File:** `frontend/src/App.jsx`
- **Change:** Add a `useEffect` hook to dynamically toggle the `light-mode` class on the `document.documentElement` based on the `darkMode` state.

### 2. Instagram-Style Bottom Navigation
- **File:** `frontend/src/index.css` & `frontend/src/App.jsx`
- **Change:** 
  - Purani upar wali tab bar ko hata kar screen ke niche (bottom) ek sleek, modern Tab Bar banayenge.
  - Icons add karenge: 👤 (Profile), 💼 (Jobs), 📚 (Learning).
  - Smooth animation aur active state glow add karenge.

### 3. New "Learning" Tab
- **File:** `frontend/src/App.jsx`
- **Change:** Naya `<LearningTab />` component banayenge jisme:
  - Interview Preparation Guides
  - Resume Tips
  - Coding resources ke cards honge.

### 4. Tinder-Style Job Swiping (Card UI)
- **File:** `frontend/src/App.jsx`
- **Change:** 
  - Jobs ko list ki jagah "Cards" mein dikhayenge.
  - "Pass" (Left/Red) aur "Save/Apply" (Right/Green) ke bade buttons honge, bilkul dating apps jaisa sleek interface.
  - Isse users ka app par time spend badhega aur experience majedar hoga.

## Verification Plan
1. App build karke Bottom Nav aur Dark mode toggle test karna.
2. Learning tab ke contents verify karna.
3. Swiping/Card buttons properly kam kar rahe hain ye check karna.
