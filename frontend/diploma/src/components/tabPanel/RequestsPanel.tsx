import {FormControl, MenuItem, Select, Stack, Typography} from "@mui/material";
import React, {useEffect, useState} from "react";
import {MetricResponse, ParseMetric} from "@/types/metricTypes";
import {getRequestsPerTime} from "@/api/metricApi";
import {CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";
import {parseMetricsResponseToData} from "@/tools/metricTools";
import {merge} from "@/tools/arrayTools";
import {timestampToDate} from "@/tools/timeTool";

const RequestsPanel = () => {


    const [value, setValue] = useState<ParseMetric>({data: [], pod_names: []})

    useEffect(() => {
        const timer = setInterval(() => {
                getRequestsPerTime().then((data) => {

                    const t = parseMetricsResponseToData(data.data)
                    if (t.data.length == 0) {
                        t.data.push({"app-deployment": 0, date: timestampToDate(Date.now() / 1000)})

                        if (value.pod_names.find((item)=>{return item == "app-deployment"}) == undefined) {
                            t.pod_names.push("app-deployment")
                        }
                    }

                    setValue({data: value.data.concat(t.data).slice(-50), pod_names: merge(value.pod_names, t.pod_names).slice(-50) })
                }).catch((err) => {
                    console.log(err)
                })
            },
            1000)
        return (
            () => {
                clearInterval(timer);
            })
    })


    return (
        <Stack>
            {value["data"].length > 0 ? <>
                <ResponsiveContainer height={600} width={"100%"}>
                <LineChart data={value["data"]}>
                    <CartesianGrid/>
                    <XAxis dataKey={"date"}/>
                    <YAxis/>
                    <Tooltip/>

                    {value.pod_names.map((item) => {
                        return (<Line type={"monotone"} dataKey={item} key={item}/>)
                    })}

                </LineChart>
            </ResponsiveContainer></> : <Typography>No data</Typography>}


        </Stack>

    );
}

export default RequestsPanel