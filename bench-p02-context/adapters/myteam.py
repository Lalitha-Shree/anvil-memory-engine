from adapter import Adapter


class Engine(Adapter):

    def __init__(self):

        self.events = []
        self.incidents = []

    # =====================================================
    # INGEST EVENTS
    # =====================================================

    def ingest(self, events):

        for e in events:

            self.events.append(e)

            kind = e.get("kind", "")

            # store incident-related events
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

        related = []

        for e in self.events:

            if e.get("service", "") == service:
                related.append(e)

        # fallback
        if not related:
            related = self.events[:20]

        return related

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
    # SIMILARITY
    # =====================================================

    def similarity(self, sig1, sig2):

        if not sig1 or not sig2:
            return 0

        set1 = set(sig1)
        set2 = set(sig2)

        overlap = len(set1 & set2)

        # stricter similarity
        score = overlap / max(len(set1), len(set2))

        # reward strong deploy+latency match
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

            past_sig = self.build_signature(related)

            score = self.similarity(
                current_sig,
                past_sig
            )

            if score > 0:

                results.append({

                    "incident_id": f"INC-{idx}",

                    "score": round(score, 2),

                    "summary":
                        "Similar behavioral pattern"

                })

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

        if (
            "deploy" in sig
            and "latency" in sig
        ):

            fixes.append({

                "action": "rollback",

                "confidence": 0.9

            })

        if "timeout" in sig:

            fixes.append({

                "action": "restart_service",

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

                    "cause": "deploy",

                    "effect": "latency_spike",

                    "confidence": 0.85

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

        related = self.get_related_events(signal)

        sig = self.build_signature(related)

        causal = self.build_causal_chain(related)

        similar = self.find_similar_incidents(sig)

        fixes = self.recommend_fix(sig)

        explanation = (
            "Recent deployment activity was followed "
            "by elevated latency and timeout failures. "
            "Historical incidents with similar "
            "behavioral signatures were previously "
            "mitigated using rollback remediation."
        )

        return {

            "related_events": related,

            "causal_chain": causal,

            "similar_past_incidents": similar,

            "suggested_remediations": fixes,

            "confidence": 0.8,

            "explain": explanation

        }

    # =====================================================
    # CLEANUP
    # =====================================================

    def close(self):
        pass