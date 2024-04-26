export interface ConfigType {
    "one_time_change": {
        "step": bigint,
    }
    "change_policy": "max" | "min" | "avg"
    "iteration_delay": bigint
    "rules": {
        "type": "date"
        "values": {
            "value": {
                "year": bigint,
                "month"?: bigint,
                "day"?: bigint,
                "hour"?: bigint,
                "minute"?: bigint,
            },
            "replicas": bigint
        }[]
    } | {
        "type": "workload",
        "metric": "request_per_second" | "total_cpu",
        "values": {
            "value": bigint,
            "replicas": bigint
        }[]
    }[]
}