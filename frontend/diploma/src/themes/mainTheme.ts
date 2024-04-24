import {createTheme} from "@mui/material";

export const mainTheme = createTheme({
    palette: {
        primary: {
            main: "rgb(0,0,0)"
        },
        secondary: {
            main: "rgb(128, 128, 128)"
        }
    },
    components: {
        MuiIconButton: {
            styleOverrides: {
                root: {
                    '&:hover, :focus, :active, :target, :visited': {
                        borderRadius: "10px"
                    },
                }
            }
        }
    }
})