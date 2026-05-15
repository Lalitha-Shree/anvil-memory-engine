from adapters.myteam_integrated import Engine
from custom.custom_events import custom_events


print("\n")
print("🚀 STARTING ADVANCED CHAOS DEMO")
print("=" * 70)

# =====================================================
# INITIALIZE ENGINE
# =====================================================

engine = Engine()

# =====================================================
# INGEST CUSTOM EVENTS
# =====================================================

print("\n")
print("📥 INGESTING CUSTOM TELEMETRY EVENTS")
print("=" * 70)

engine.ingest(custom_events)

print(f"Total Events Loaded : {len(custom_events)}")

# =====================================================
# FIND INCIDENT SIGNAL
# =====================================================

signal = None

for e in custom_events:

    if e.get("kind") == "incident_signal":

        signal = e
        break

# =====================================================
# RUN AI ANALYSIS
# =====================================================

print("\n")
print("🧠 RUNNING AI OPERATIONAL ANALYSIS")
print("=" * 70)

result = engine.reconstruct_context(signal)

# =====================================================
# FINAL RESULT
# =====================================================

print("\n")
print("=" * 70)
print("✅ FINAL AI CONTEXT OUTPUT")
print("=" * 70)

print(result)

print("\n")
print("🎯 DEMO COMPLETE")
print("=" * 70)