import {MetricResponse, ParseMetric} from "@/types/metricTypes";
import {timestampToDate} from "@/tools/timeTool";

export const parseMetricsResponseToData = (dt: MetricResponse): ParseMetric => {

    const res: { [_: string]: number | string }[] = []

    const names: string[] = []
    if (dt.values.length > 0) {

        const t: { [_: string]: number | string } = {}
        for (let j = 0; j < dt.values.length; j++) {
            t[dt.values[j].metric.kubernetes_pod_name] = Number(dt.values[j].value[1]) / 60
            if (names.length < dt.values.length) {
                names.push(dt.values[j].metric.kubernetes_pod_name)
            }
        }

        t["date"] = timestampToDate(dt.values[0].value[0])

        res.push(t)

    }
    return {
        "data": res,
        "pod_names": names
    }
}