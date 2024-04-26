import axios from "axios";
import {ConfigType} from "@/types/configTypes";


export const getConfig = async () => {
    return axios.get("/api/v1/config")
}

export const setConfig = async (config: ConfigType) => {
    return axios.post("/api/v1/config", config)
}