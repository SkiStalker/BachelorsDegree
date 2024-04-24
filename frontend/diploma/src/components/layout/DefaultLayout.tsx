import React from "react";
import Header from "@/components/header/Header";
import Footer from "@/components/footer/Footer";
import {Stack} from "@mui/material";

export default function Layout({children}: { children: React.ReactElement }) {
    return (
        <Stack sx={{width: "calc(100vw - 100px)", height: "calc(100vh - 40px)", display: "flex", flexDirection: "column", padding: "20px"}} spacing={8}>
            <Header/>
            <main style={{flexGrow: 1}}>{children}</main>
            <Footer/>
        </Stack>
    )
}