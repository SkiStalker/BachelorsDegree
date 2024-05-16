import {AutoDataRequest, AutoDataType} from "@/types/autoDataTypes";
import axios from "axios";

export const getAutoInfo = async (data: AutoDataRequest) => {

    return axios.get<{"data": AutoDataType[]}>("/api/v1/auto_info", { params: data });
}