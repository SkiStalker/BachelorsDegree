import React, {ReactElement, ReactNode} from 'react'
import type {NextPage} from 'next'
import type {AppProps} from 'next/app'
import "@/styles/styles.css"
import {ThemeProvider} from "@mui/material";
import {mainTheme} from "@/themes/mainTheme";
import Layout from "@/components/layout/DefaultLayout";

type NextPageWithLayout = NextPage & {
    getLayout?: (page: ReactElement) => ReactNode
}

type AppPropsWithLayout = AppProps & {
    Component: NextPageWithLayout
}


function App({Component, pageProps}: AppPropsWithLayout) {
    const getLayout = Component.getLayout ?? ((page) => {
        return <Layout>{page}</Layout>
    })

    return (
            <ThemeProvider theme={mainTheme}>
                {getLayout(<Component  {...pageProps} />)}
            </ThemeProvider>)
}


export default App