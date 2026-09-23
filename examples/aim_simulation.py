from collections import Counter
from src.aim_simulator import simulate_magazine

shots = simulate_magazine(30, seed=42)
counts = Counter(shots)

print("Simulated magazine:")
for result in ("miss", "torso", "head"):
    print(f"{result:>6}: {counts[result]}")
