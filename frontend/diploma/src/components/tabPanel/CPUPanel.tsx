import {FormControl, MenuItem, Select, Stack, Typography} from "@mui/material";
import {useEffect, useState} from "react";
import {MetricResponse, ParseMetric} from "@/types/metricTypes";
import {getRequestsPerTime, getTotalCPUUsage} from "@/api/metricApi";
import {CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";
import {parseMetricsResponseToData} from "@/tools/metricTools";

const CPUPanel = () => {

    const [curValue, setCurValue] = useState("1h")


    const [value, setValue] = useState<ParseMetric>({data: [], pod_names: []})

    useEffect(() => {
        const timer = setInterval(() => {
                getTotalCPUUsage({"interval": curValue as "5s" | "1m" | "1h" | "1d"}).then((data) => {
                    setValue(parseMetricsResponseToData(data.data))
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
            <FormControl>
                <Select value={curValue} onChange={(e) => {
                    setCurValue(e.target.value)
                }} sx={{width: "10%", alignSelf: "flex-end"}}>
                    <MenuItem value={"5s"}>Second</MenuItem>
                    <MenuItem value={"1m"}>Minute</MenuItem>
                    <MenuItem value={"1h"}>Hour</MenuItem>
                    <MenuItem value={"1d"}>Day</MenuItem>
                </Select>
            </FormControl>
            {value["data"].length > 0 ? <>            <ResponsiveContainer height={600} width={"100%"}>
                <LineChart data={value["data"]}>
                    <CartesianGrid/>
                    <XAxis dataKey={"date"}/>
                    <YAxis/>

                    {value.pod_names.map((item) => {
                        return (<Line type={"monotone"} dataKey={item} key={item} dot={<></>}/>)
                    })}

                </LineChart>
            </ResponsiveContainer></> : <Typography>No data</Typography>}


        </Stack>

    );
}

export default CPUPanel