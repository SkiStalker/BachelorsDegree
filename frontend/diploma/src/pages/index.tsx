import {Button, IconButton, Stack, Typography} from "@mui/material";
import SettingsIcon from '@mui/icons-material/Settings';
import Link from "next/link"
import TabPanel from "@/components/tabPanel/TabPanel";


const MainPage = () => {
    return (<Stack height={"100%"} width={"100%"}>
        <Stack direction={"row"}>
            <Link href={"/config"}>
                <IconButton>
                    <SettingsIcon/>
                    <Typography sx={{paddingLeft: "10px"}}>
                        {"Настроить конфигурацию"}
                    </Typography>
                </IconButton>
            </Link>
        </Stack>
        <Stack>
            <TabPanel/>
        </Stack>

    </Stack>)
}

export default MainPage