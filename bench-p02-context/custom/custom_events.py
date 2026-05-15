custom_events = [

    # =====================================================
    # TOPOLOGY DRIFT
    # =====================================================

    {
        "kind": "deploy",
        "service": "checkout-v2",
        "ts": 100
    },

    # old service name
    {
        "kind": "log",
        "service": "checkout-service",
        "msg": "legacy service redirect",
        "ts": 101
    },

    # =====================================================
    # LATENCY SPIKE
    # =====================================================

    {
        "kind": "metric",
        "service": "checkout-v2",
        "name": "latency",
        "value": 1200,
        "ts": 102
    },

    # =====================================================
    # TIMEOUTS
    # =====================================================

    {
        "kind": "log",
        "service": "checkout-v2",
        "msg": "timeout error detected",
        "ts": 103
    },

    # =====================================================
    # INCIDENT SIGNAL
    # =====================================================

    {
        "kind": "incident_signal",
        "incident_id": "INC-900",
        "service": "checkout-v2",
        "ts": 104
    },

    # =====================================================
    # RETRY STORM
    # =====================================================

    {
        "kind": "log",
        "service": "payment-core",
        "msg": "retry storm detected",
        "ts": 105
    },

    # =====================================================
    # CPU OVERLOAD
    # =====================================================

    {
        "kind": "metric",
        "service": "payment-core",
        "name": "cpu",
        "value": 97,
        "ts": 106
    },

    # =====================================================
    # DATABASE OVERLOAD
    # =====================================================

    {
        "kind": "metric",
        "service": "inventory-db",
        "name": "memory",
        "value": 92,
        "ts": 107
    },

    # =====================================================
    # API GATEWAY FAILURE
    # =====================================================

    {
        "kind": "metric",
        "service": "api-gateway",
        "name": "latency",
        "value": 1500,
        "ts": 108
    },

    # =====================================================
    # NOTIFICATION BACKLOG
    # =====================================================

    {
        "kind": "log",
        "service": "notification-worker",
        "msg": "queue backlog overload",
        "ts": 109
    },

    # =====================================================
    # NOISY TELEMETRY
    # =====================================================

    {
        "kind": "log",
        "service": "search-engine",
        "msg": "heartbeat ok",
        "ts": 110
    },

    {
        "kind": "log",
        "service": "recommendation-ai",
        "msg": "cache refresh success",
        "ts": 111
    },

    # =====================================================
    # FALSE POSITIVE
    # =====================================================

    {
        "kind": "metric",
        "service": "region-eu-west",
        "name": "cpu",
        "value": 88,
        "ts": 112
    },

    # =====================================================
    # PARTIAL RECOVERY
    # =====================================================

    {
        "kind": "remediation",
        "service": "payment-core",
        "action": "restart_service",
        "ts": 113
    },

    # =====================================================
    # ROLLBACK
    # =====================================================

    {
        "kind": "remediation",
        "service": "checkout-v2",
        "action": "rollback",
        "ts": 114
    },

    # =====================================================
    # MULTI REGION FAILURE
    # =====================================================

    {
        "kind": "metric",
        "service": "region-us-east",
        "name": "latency",
        "value": 1700,
        "ts": 115
    },

    # =====================================================
    # DELAYED LOG
    # =====================================================

    {
        "kind": "log",
        "service": "auth-service",
        "msg": "authentication timeout",
        "ts": 90
    }

]