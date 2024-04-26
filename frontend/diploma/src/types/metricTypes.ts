export interface MetricInterval {
    "interval": "5s" | "1m" | "1h" | "1d"
}


export interface MetricResponse {
    "values": {
        "metric": {
            "__name__": string,
            "app": string,
            "instance": string,
            "job": string,
            "kubernetes_namespace": string,
            "kubernetes_pod_name": string,
            "pod_template_hash": string
        }
        "values": string & number[]
    }[]
}

export interface PodsCountResponse {
    pods_count: number
}


export interface ParseMetric {
    "data": { [_: string]: number }[]

    "pod_names": string[]

}


export interface ParsePodsCount {
    "data": {
        "pods_count": number,
        "date": number
    }[]

}