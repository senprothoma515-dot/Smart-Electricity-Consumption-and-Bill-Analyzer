
import heapq

print("======================================")
print(" APPLIANCE CONSUMPTION ANALYZER")
print("======================================")

# Appliance name and monthly electricity consumption
appliances = [
    ("Air Conditioner", 90),
    ("Electric Heater", 75),
    ("Refrigerator", 35),
    ("Television", 15),
    ("Washing Machine", 25)
]

# Create a priority queue
priority_queue = []

for name, units in appliances:
    # Negative units make the largest value come out first
    heapq.heappush(priority_queue, (-units, name))

print("\nAppliances: Highest Consumption First")

rank = 1

while priority_queue:
    negative_units, name = heapq.heappop(priority_queue)
    units = -negative_units

    print(rank, ".", name, "-", units, "units")
    rank += 1
