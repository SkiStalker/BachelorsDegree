import {useRouter} from "next/router";
import React from "react";
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link';
import {Typography} from "@mui/material";
import {breadcrumbsMap} from "@/config/breadcrumbsConfig";


const Header = () => {

    const router = useRouter();

    const path = router.asPath.split("/")


    if (path[path.length - 1] !== "") {
        path.unshift("")
    }
    return (<Breadcrumbs>
        {
            path.slice(1).map((item, ind, arr) => {
                if (ind !== arr.length - 1) {
                    return <Link underline={"hover"} key={ind} color="inherit"
                                 onClick={async ()=>{
                                     await router.push(breadcrumbsMap[item as keyof typeof breadcrumbsMap]?.link || "/")
                                 }}>
                        <Typography fontSize={20}>
                            {breadcrumbsMap[item as keyof typeof breadcrumbsMap]?.name || item}
                        </Typography>
                    </Link>
                }
                return <Typography fontSize={20}
                                   key={ind}>{breadcrumbsMap[item as keyof typeof breadcrumbsMap]?.name || item}</Typography>

            })
        }
    </Breadcrumbs>)
}

export default Header