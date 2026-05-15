from collections import defaultdict


class EventStore:

    def __init__(self):

        # master storage
        self.events = []

        # indexes
        self.by_kind = defaultdict(list)
        self.by_service = defaultdict(list)
        self.by_incident = defaultdict(list)

        # incident signals
        self.incident_signals = {}

    # =====================================================
    # ADD EVENTS
    # =====================================================

    def add_events(self, events):

        for event in events:

            # store globally
            self.events.append(event)

            # -----------------------------
            # index by kind
            # -----------------------------
            kind = event.get("kind")

            if kind:
                self.by_kind[kind].append(event)

            # -----------------------------
            # index by service
            # -----------------------------
            service = event.get("service")

            if service:
                self.by_service[service].append(event)

            # -----------------------------
            # index by incident
            # -----------------------------
            incident_id = event.get(
                "incident_id"
            )

            if incident_id:
                self.by_incident[
                    incident_id
                ].append(event)

            # -----------------------------
            # save incident signal
            # -----------------------------
            if (
                kind == "incident_signal"
                and incident_id
            ):

                self.incident_signals[
                    incident_id
                ] = event

    # =====================================================
    # EVENTS BY KIND
    # =====================================================

    def get_events_by_kind(self, kind):

        return self.by_kind.get(
            kind,
            []
        )

    # =====================================================
    # EVENTS BY SERVICE
    # =====================================================

    def get_events_by_service(
        self,
        service
    ):

        return self.by_service.get(
            service,
            []
        )

    # =====================================================
    # EVENTS BY INCIDENT
    # =====================================================

    def get_events_by_incident(
        self,
        incident_id
    ):

        return self.by_incident.get(
            incident_id,
            []
        )

    # =====================================================
    # INCIDENT WINDOW
    # =====================================================

    def get_incident_window(
        self,
        incident_id,
        window=50
    ):

        signal = self.incident_signals.get(
            incident_id
        )

        if not signal:
            return []

        service = signal.get(
            "service"
        )

        ts = signal.get(
            "ts",
            0
        )

        candidates = self.by_service.get(
            service,
            []
        )

        result = []

        for event in candidates:

            try:

                event_ts = int(
                    event.get("ts", 0)
                )

                ts_int = int(ts)

                if abs(
                    event_ts - ts_int
                ) <= window:

                    result.append(event)

            except:
                pass

        return sorted(

            result,

            key=lambda e: int(
                e.get("ts", 0)
            )

        )

    # =====================================================
    # RECENT EVENTS
    # =====================================================

    def get_recent_events(
        self,
        service,
        limit=10
    ):

        events = self.by_service.get(
            service,
            []
        )

        try:

            return sorted(

                events,

                key=lambda e: int(
                    e.get("ts", 0)
                ),

                reverse=True

            )[:limit]

        except:

            return events[:limit]