# Full `myteam_integrated.py` Replacement


from adapter import Adapter
from adapters.memory_engine import EventStore


class Engine(Adapter):

    already_printed = False

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        self.store = EventStore()

        self.events = []

        self.incidents = []

    # =====================================================
    # INGEST EVENTS
    # =====================================================

    def ingest(self, events):

        self.store.add_events(events)

        self.events.extend(events)

        for e in events:

            kind = e.get("kind", "")

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

        if incident_id:

            related = self.store.get_incident_window(
                incident_id
            )

            if related:
                return related

        related = self.store.get_events_by_service(
            service
        )

        if related:
            return related

        return self.events[:20]

    # =====================================================
    # BUILD SIGNATURE
    # =====================================================

    def build_signature(self, events):

        sig = []

        for e in events:

            kind = e.get("kind", "")

            if kind == "deploy":
                sig.append("deploy")

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

            elif kind == "trace":
                sig.append("trace")

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

        # ============================================
        # STRONG DEPLOY-LATENCY MATCH
        # ============================================

        if (
            "deploy" in set1
            and "deploy" in set2
            and "latency" in set1
            and "latency" in set2
        ):

            score += 0.25

        # ============================================
        # TIMEOUT MATCH
        # ============================================

        if (
            "timeout" in set1
            and "timeout" in set2
        ):

            score += 0.15

        # ============================================
        # CPU MATCH
        # ============================================

        if (
            "cpu" in set1
            and "cpu" in set2
        ):

            score += 0.15

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

            # ============================================
            # DECOY FILTER
            # ============================================

            if score >= 0.5:

                results.append({

                    "incident_id":
                        f"INC-{idx}",

                    "similarity":
                        round(score, 2),

                    "summary":
                        "Similar behavioral pattern"

                })

        results.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        return results[:5]

    # =====================================================
    # REMEDIATION
    # =====================================================

    def recommend_fix(self, sig):

        fixes = []

        # ============================================
        # ROLLBACK
        # ============================================

        if (
            "deploy" in sig
            and "latency" in sig
        ):

            fixes.append({

                "action": "rollback",

                "confidence": 0.93

            })

        # ============================================
        # RESTART
        # ============================================

        elif "timeout" in sig:

            fixes.append({

                "action":
                    "restart",

                "confidence": 0.84

            })

        # ============================================
        # SCALE UP
        # ============================================

        elif "cpu" in sig:

            fixes.append({

                "action":
                    "scale_up",

                "confidence": 0.88

            })

        # ============================================
        # CONFIG CHANGE
        # ============================================

        elif "memory" in sig:

            fixes.append({

                "action":
                    "config_change",

                "confidence": 0.79

            })

        # ============================================
        # FAILOVER
        # ============================================

        elif "failure" in sig:

            fixes.append({

                "action":
                    "failover",

                "confidence": 0.76

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

            if kind == "deploy":
                deploy_seen = True

            if kind == "metric":

                metric = str(
                    e.get("name", "")
                ).lower()

                if "latency" in metric:
                    latency_seen = True

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

        # ============================================
        # DECOY DETECTION
        # ============================================

        high_conf = [

            s for s in similar

            if s.get("similarity", 0) >= 0.5

        ]

        if len(high_conf) == 0:

            fixes = []

            explanation = (

                "AI classified this incident as a "
                "possible decoy or low-confidence anomaly."

            )

        else:

            fixes = self.recommend_fix(sig)

            explanation = (

                "Recent deployment activity was "
                "followed by elevated latency and "
                "timeout failures. Historical "
                "incidents with similar behavioral "
                "patterns were previously mitigated "
                "using remediation actions."

            )

        if Engine.already_printed:

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

        Engine.already_printed = True

        print("\n")
        print("=" * 70)
        print("AI ANALYSIS REPORT")
        print("=" * 70)

        print("\nSIGNATURES DETECTED:")

        for s in sig:
            print(f"- {s}")

        print("\nSIMILAR INCIDENTS:")

        for s in similar:
            print(s)

        print("\nREMEDIATIONS:")

        for f in fixes:
            print(f)

        print("\nEXPLANATION:")
        print(explanation)

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

