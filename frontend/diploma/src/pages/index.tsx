import {Button, IconButton, Stack, Typography} from "@mui/material";
import SettingsIcon from '@mui/icons-material/Settings';

const MainPage = () => {
    return (<Stack height={"100%"} width={"100%"}>
        <Stack direction={"row"}>
            <IconButton>
                <SettingsIcon/>
                <Typography sx={{paddingLeft: "10px"}}>
                    {"Настроить конфигурацию"}
                </Typography>
            </IconButton>
        </Stack>
        <Stack>

        </Stack>

    </Stack>)
}

export default MainPage