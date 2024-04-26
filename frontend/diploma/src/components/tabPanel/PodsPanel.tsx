import {FormControl, MenuItem, Select, Stack, Typography} from "@mui/material";
import React, {useEffect, useState} from "react";
import {MetricResponse, ParseMetric, ParsePodsCount} from "@/types/metricTypes";
import {getPodsCount, getRequestsPerTime} from "@/api/metricApi";
import {CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";
import {parseMetricsResponseToData} from "@/tools/metricTools";

const PodsPanel = () => {

    const [value, setValue] = useState<{ "date": number, "pods_count": number }[]>([])

    useEffect(() => {
        const timer = setInterval(() => {
                getPodsCount().then((data) => {
                    setValue([...value, {pods_count: data.data.pods_count, date: Date.now()}])
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
            {value.length > 0 ? <>            <ResponsiveContainer height={600} width={"100%"}>
                <LineChart data={value}>
                    <CartesianGrid/>
                    <XAxis dataKey={"date"}/>
                    <YAxis domain={["dataMin - 10", "dataMax + 10"]}/>
                    <Tooltip/>
                    <Line type={"monotone"} dataKey={"pods_count"} dot={<></>}/>

                </LineChart>
            </ResponsiveContainer></> : <Typography>No data</Typography>}
        </Stack>

    );
}

export default PodsPanel