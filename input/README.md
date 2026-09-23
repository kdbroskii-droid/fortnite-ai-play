# Input module

This directory contains the platform-neutral input vocabulary and macro definition.

The AI should emit an **action plan**, not raw OS events:

`AI -> validator -> macro/action executor`

The validator should reject unknown keys, negative delays, malformed mouse events, and unsafe/unbounded macro loops.

A future executor can target a test harness or an explicitly supported input backend. Device masquerading and anti-detection behavior are deliberately out of scope.
