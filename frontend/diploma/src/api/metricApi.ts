import axios from "axios";
import {MetricInterval, MetricResponse, PodsCountResponse} from "@/types/metricTypes";

export const getRequestsPerTime = async (metricInterval: MetricInterval) => {
    return axios.get<MetricResponse>("/api/v1/requests_stat", {
        params: {...metricInterval}
    })
}

export const getTotalCPUUsage = async (metricInterval: MetricInterval) => {
    return axios.get<MetricResponse>("/api/v1/cpu_stat", {
        params: {...metricInterval}
    })
}

export const getPodsCount = async () => {

    return axios.get<PodsCountResponse>("/api/v1/pods_count")
}