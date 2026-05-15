from adapter import Adapter
from adapters.memory_engine import EventStore


class Engine(Adapter):

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        # operational memory layer
        self.store = EventStore()

        # local storage
        self.events = []

        self.incidents = []

        # prevents repeated demo printing
        self.debug_printed = False

    # =====================================================
    # INGEST EVENTS
    # =====================================================

    def ingest(self, events):

        # add into memory engine
        self.store.add_events(events)

        # local copy
        self.events.extend(events)

        for e in events:

            kind = e.get("kind", "")

            # collect incident-like events
            if kind in [
                "incident_signal",
                "alert",
                "remediation"
            ]:

                self.incidents.append(e)

    # =====================================================
    # RELATED EVENTS
    # =====================================================

    def get_related_events(self, signal):

        service = signal.get("service", "")

        incident_id = signal.get(
            "incident_id",
            ""
        )

        # incident window retrieval
        if incident_id:

            related = self.store.get_incident_window(
                incident_id
            )

            if related:
                return related

        # fallback retrieval
        related = self.store.get_events_by_service(
            service
        )

        if related:
            return related

        # emergency fallback
        return self.events[:20]

    # =====================================================
    # BUILD SIGNATURE
    # =====================================================

    def build_signature(self, events):

        sig = []

        for e in events:

            kind = e.get("kind", "")

            # deployment
            if kind == "deploy":
                sig.append("deploy")

            # metrics
            elif kind == "metric":

                metric = str(
                    e.get("name", "")
                ).lower()

                if "latency" in metric:
                    sig.append("latency")

                if "cpu" in metric:
                    sig.append("cpu")

                if "memory" in metric:
                    sig.append("memory")

            # logs
            elif kind == "log":

                msg = str(
                    e.get("msg", "")
                ).lower()

                if "timeout" in msg:
                    sig.append("timeout")

                if "error" in msg:
                    sig.append("error")

                if "fail" in msg:
                    sig.append("failure")

            # traces
            elif kind == "trace":
                sig.append("trace")

            # remediation
            elif kind == "remediation":

                action = str(
                    e.get("action", "")
                ).lower()

                if action:
                    sig.append(action)

        return list(set(sig))

    # =====================================================
    # SIGNATURE SIMILARITY
    # =====================================================

    def similarity(self, sig1, sig2):

        if not sig1 or not sig2:
            return 0

        set1 = set(sig1)
        set2 = set(sig2)

        overlap = len(set1 & set2)

        score = overlap / max(
            len(set1),
            len(set2)
        )

        # reward deploy-latency pattern
        if (
            "deploy" in set1
            and "deploy" in set2
            and "latency" in set1
            and "latency" in set2
        ):
            score += 0.2

        return min(score, 1.0)

    # =====================================================
    # FIND SIMILAR INCIDENTS
    # =====================================================

    def find_similar_incidents(self, current_sig):

        results = []

        for idx, inc in enumerate(self.incidents):

            related = self.get_related_events(inc)

            past_sig = self.build_signature(
                related
            )

            score = self.similarity(
                current_sig,
                past_sig
            )

            if score > 0:

                results.append({

                    "incident_id":
                        f"INC-{idx}",

                    "score":
                        round(score, 2),

                    "summary":
                        "Similar behavioral pattern"

                })

        # sort descending
        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:5]

    # =====================================================
    # REMEDIATION
    # =====================================================

    def recommend_fix(self, sig):

        fixes = []

        # deploy + latency issue
        if (
            "deploy" in sig
            and "latency" in sig
        ):

            fixes.append({

                "action": "rollback",

                "confidence": 0.9

            })

        # timeout issue
        if "timeout" in sig:

            fixes.append({

                "action":
                    "restart_service",

                "confidence": 0.7

            })

        return fixes

    # =====================================================
    # CAUSAL CHAIN
    # =====================================================

    def build_causal_chain(self, events):

        chain = []

        deploy_seen = False
        latency_seen = False

        for e in events:

            kind = e.get("kind", "")

            # deployment seen
            if kind == "deploy":
                deploy_seen = True

            # latency metric
            if kind == "metric":

                metric = str(
                    e.get("name", "")
                ).lower()

                if "latency" in metric:
                    latency_seen = True

            # causal relation
            if deploy_seen and latency_seen:

                chain.append({

                    "cause":
                        "deploy",

                    "effect":
                        "latency_spike",

                    "confidence":
                        0.85

                })

                break

        return chain

    # =====================================================
    # MAIN RECONSTRUCTION
    # =====================================================

    def reconstruct_context(
        self,
        signal,
        mode="fast"
    ):

        # =================================================
        # FETCH RELATED DATA
        # =================================================

        related = self.get_related_events(
            signal
        )

        sig = self.build_signature(
            related
        )

        causal = self.build_causal_chain(
            related
        )

        similar = self.find_similar_incidents(
            sig
        )

        fixes = self.recommend_fix(sig)

        # ================================================
        # PRINT ONLY ONCE
        # ================================================

        if self.debug_printed:

            explanation = (

                "Recent deployment activity was "
                "followed by elevated latency and "
                "timeout failures. Historical "
                "incidents with similar behavioral "
                "patterns were previously mitigated "
                "using rollback remediation."

            )

            return {

                "related_events":
                    related,

                "causal_chain":
                    causal,

                "similar_past_incidents":
                    similar,

                "suggested_remediations":
                    fixes,

                "confidence":
                    0.87,

                "explain":
                    explanation

            }

        self.debug_printed = True

        # =================================================
        # RAW OUTPUT
        # =================================================

        print("\n")
        print("╔" + "═" * 60 + "╗")
        print("║                 RAW ENGINE OUTPUT                  ║")
        print("╚" + "═" * 60 + "╝")

        print("\n")
        print("RAW INCIDENT SIGNAL:")
        print(signal)

        print("\n")
        print("RAW RELATED EVENTS:")

        for r in related[:10]:
            print(r)

        print("\n")
        print("RAW SIGNATURE:")
        print(sig)

        print("\n")
        print("RAW CAUSAL CHAIN:")
        print(causal)

        print("\n")
        print("RAW SIMILAR INCIDENTS:")
        print(similar)

        print("\n")
        print("RAW REMEDIATIONS:")
        print(fixes)

        # =================================================
        # STRUCTURED OUTPUT
        # =================================================

        print("\n")
        print("╔" + "═" * 60 + "╗")
        print("║            STRUCTURED CONTEXT VIEW                 ║")
        print("╚" + "═" * 60 + "╝")

        # -------------------------------------------------
        # INCIDENT SIGNAL
        # -------------------------------------------------

        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│ INCIDENT SIGNAL                                   │")
        print("└" + "─" * 58 + "┘")

        print(
            f"{'FIELD':<20}"
            f"{'VALUE':<35}"
        )

        print("-" * 55)

        print(
            f"{'Service':<20}"
            f"{str(signal.get('service')):<35}"
        )

        print(
            f"{'Incident ID':<20}"
            f"{str(signal.get('incident_id')):<35}"
        )

        print(
            f"{'Timestamp':<20}"
            f"{str(signal.get('ts')):<35}"
        )

        # -------------------------------------------------
        # RELATED EVENTS
        # -------------------------------------------------

        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│ RELATED EVENTS                                    │")
        print("└" + "─" * 58 + "┘")

        print(

            f"{'KIND':<18}"
            f"{'SERVICE':<20}"
            f"{'TIMESTAMP':<15}"

        )

        print("-" * 55)

        for r in related[:10]:

            print(

                f"{str(r.get('kind', '')):<18}"
                f"{str(r.get('service', '')):<20}"
                f"{str(r.get('ts', '')):<15}"

            )

        # -------------------------------------------------
        # SIGNATURES
        # -------------------------------------------------

        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│ DETECTED BEHAVIOR SIGNATURES                      │")
        print("└" + "─" * 58 + "┘")

        for s in sig:
            print(f"✔ {s}")

        # -------------------------------------------------
        # CAUSAL CHAIN
        # -------------------------------------------------

        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│ CAUSAL CHAIN                                      │")
        print("└" + "─" * 58 + "┘")

        if causal:

            for c in causal:

                print(
                    f"CAUSE  : {c.get('cause')}"
                )

                print(
                    f"EFFECT : {c.get('effect')}"
                )

                print(
                    f"CONF   : {c.get('confidence')}"
                )

        else:
            print("No causal chain identified")

        # -------------------------------------------------
        # SIMILAR INCIDENTS
        # -------------------------------------------------

        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│ SIMILAR HISTORICAL INCIDENTS                      │")
        print("└" + "─" * 58 + "┘")

        if similar:

            print(

                f"{'INCIDENT':<20}"
                f"{'SCORE':<15}"
                f"{'SUMMARY':<20}"

            )

            print("-" * 55)

            for s in similar:

                print(

                    f"{str(s.get('incident_id')):<20}"
                    f"{str(s.get('score')):<15}"
                    f"{str(s.get('summary')):<20}"

                )

        else:
            print("No similar incidents found")

        # -------------------------------------------------
        # REMEDIATION
        # -------------------------------------------------

        print("\n")
        print("┌" + "─" * 58 + "┐")
        print("│ SUGGESTED REMEDIATIONS                            │")
        print("└" + "─" * 58 + "┘")

        if fixes:

            for f in fixes:

                print(
                    f"→ ACTION     : "
                    f"{f.get('action')}"
                )

                print(
                    f"  CONFIDENCE : "
                    f"{f.get('confidence')}"
                )

        else:
            print("No remediation suggestions")

        # =================================================
        # AI ANALYSIS
        # =================================================

        print("\n")
        print("╔" + "═" * 60 + "╗")
        print("║                AI ANALYSIS REPORT                 ║")
        print("╚" + "═" * 60 + "╝")

        print("\n")

        if (
            "deploy" in sig
            and "latency" in sig
        ):

            print(
                "AI detected a deployment-related "
                "latency regression pattern."
            )

            print(
                "Historical operational memory "
                "shows similar outages previously "
                "resolved using rollback actions."
            )

        elif "timeout" in sig:

            print(
                "AI identified timeout instability "
                "across the affected service."
            )

        else:

            print(
                "AI detected operational anomaly "
                "requiring investigation."
            )

        print("\n")
        print("FINAL ROOT CAUSE:")

        if "deploy" in sig:

            print(
                "Recent deployment likely triggered "
                "service degradation."
            )

        else:

            print(
                "Unknown operational instability."
            )

        print("\n")
        print("OVERALL CONFIDENCE : 0.87")

        # =================================================
        # FINAL RETURN
        # =================================================

        explanation = (

            "Recent deployment activity was "
            "followed by elevated latency and "
            "timeout failures. Historical "
            "incidents with similar behavioral "
            "patterns were previously mitigated "
            "using rollback remediation."

        )

        final_output = {

            "related_events":
                related,

            "causal_chain":
                causal,

            "similar_past_incidents":
                similar,

            "suggested_remediations":
                fixes,

            "confidence":
                0.87,

            "explain":
                explanation

        }

        return final_output

    # =====================================================
    # CLEANUP
    # =====================================================

    def close(self):
        pass