import {AutoDataRequest, AutoDataResponse, AutoDataType} from "@/types/autoDataTypes";
import axios from "axios";

export const getAutoInfo = async (data: AutoDataRequest) => {

    return axios.get<AutoDataResponse>("/api/v1/auto_info", { params: data });
}