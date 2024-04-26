import {MetricResponse, ParseMetric} from "@/types/metricTypes";

export const parseMetricsResponseToData = (dt: MetricResponse): ParseMetric => {

    const res: { [_: string]: number }[] = []

    const names: string[] = []

    if (dt.values.length > 0) {
        for (let i = 0; i < dt.values[0].values.length; i++) {
            const t: { [_: string]: number } = {}
            for (let j = 0; j < dt.values.length; j++) {

                t[dt.values[j].metric.kubernetes_pod_name] = dt.values[j].values[i][1]

                if (res.length < dt.values.length) {
                    names.push(dt.values[j].metric.kubernetes_pod_name)
                }
            }

            t["date"] = dt.values[0].values[i][0]

            res.push(t)
        }
    }
    return {
        "data": res,
        "pod_names": names
    }
}