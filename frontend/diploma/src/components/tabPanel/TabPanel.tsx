import React, {useState} from "react";
import {Box, Tab, Tabs, Typography} from "@mui/material";
import RequestsPanel from "@/components/tabPanel/RequestsPanel";
import CPUPanel from "@/components/tabPanel/CPUPanel";
import PodsPanel from "@/components/tabPanel/PodsPanel";
import DataPanel from "@/components/tabPanel/DataPanel";

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function CustomTabPanel(props: TabPanelProps) {
    const {children, value, index, ...other} = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{p: 3}}>
                    {children}
                </Box>
            )}
        </div>
    );
}


const TabPanel = () => {
    const [curTab, setCurTab] = useState(0)


    return (
        <>
            <Box sx={{borderBottom: 1, borderColor: 'divider'}}>
                <Tabs value={curTab} onChange={(event, value) => {
                    setCurTab(value)
                }}>
                    <Tab label="Полученные данные"/>
                    <Tab label="Запросы в секунду"/>
                    <Tab label="Использование CPU"/>
                    <Tab label="Количество POD's"/>
                </Tabs>

            </Box>

            <CustomTabPanel index={0} value={curTab}>
                <DataPanel/>
            </CustomTabPanel>

            <CustomTabPanel index={1} value={curTab}>
                <RequestsPanel/>
            </CustomTabPanel>

            <CustomTabPanel index={2} value={curTab}>
                <CPUPanel/>
            </CustomTabPanel>

            <CustomTabPanel index={3} value={curTab}>
                <PodsPanel/>
            </CustomTabPanel></>
    );
}

export default TabPanel;