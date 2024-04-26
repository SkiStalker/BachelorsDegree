import {CircularProgress, Stack} from "@mui/material";

const Loader = () => {
    return (
        <Stack sx={{width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}><CircularProgress/></Stack>)
}

export default Loader