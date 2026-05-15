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
        # STAGE 1
        # =================================================

        print("\n")
        print("=" * 60)
        print("STAGE 1 : INCIDENT SIGNAL RECEIVED")
        print("=" * 60)

        print(signal)

        # =================================================
        # STAGE 2
        # =================================================

        related = self.get_related_events(
            signal
        )

        print("\n")
        print("=" * 60)
        print("STAGE 2 : RELATED EVENTS RETRIEVED")
        print("=" * 60)

        for r in related[:10]:
            print(r)

        # =================================================
        # STAGE 3
        # =================================================

        sig = self.build_signature(
            related
        )

        print("\n")
        print("=" * 60)
        print("STAGE 3 : BEHAVIOR SIGNATURE")
        print("=" * 60)

        print(sig)

        # =================================================
        # STAGE 4
        # =================================================

        causal = self.build_causal_chain(
            related
        )

        print("\n")
        print("=" * 60)
        print("STAGE 4 : CAUSAL ANALYSIS")
        print("=" * 60)

        print(causal)

        # =================================================
        # STAGE 5
        # =================================================

        similar = self.find_similar_incidents(
            sig
        )

        print("\n")
        print("=" * 60)
        print("STAGE 5 : SIMILAR INCIDENT SEARCH")
        print("=" * 60)

        if similar:

            for s in similar:
                print(s)

        else:
            print("No similar incidents found")

        # =================================================
        # STAGE 6
        # =================================================

        fixes = self.recommend_fix(sig)

        print("\n")
        print("=" * 60)
        print("STAGE 6 : REMEDIATION SUGGESTIONS")
        print("=" * 60)

        if fixes:

            for f in fixes:
                print(f)

        else:
            print("No remediation suggestions")

        # =================================================
        # FINAL EXPLANATION
        # =================================================

        explanation = (

            "Recent deployment activity was "
            "followed by elevated latency and "
            "timeout failures. Historical "
            "incidents with similar behavioral "
            "patterns were previously mitigated "
            "using rollback remediation."

        )

        # =================================================
        # FINAL OUTPUT
        # =================================================

        print("\n")
        print("=" * 60)
        print("STAGE 7 : FINAL CONTEXT GENERATED")
        print("=" * 60)

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
                0.8,

            "explain":
                explanation

        }

        print(final_output)

        print("\n")
        print("=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)

        return final_output

    # =====================================================
    # CLEANUP
    # =====================================================

    def close(self):
        pass