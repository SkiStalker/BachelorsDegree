import axios from "axios";
import {MetricInterval, MetricResponse, PodsCountResponse} from "@/types/metricTypes";

export const getRequestsPerTime =  async () => {
    return axios.get<MetricResponse>("/api/v1/requests_stat")
}

export const getTotalCPUUsage = async () => {
    return axios.get<MetricResponse>("/api/v1/cpu_stat")
}

export const getPodsCount = async () => {

    return axios.get<PodsCountResponse>("/api/v1/pods_count")
}