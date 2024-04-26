import React, {SyntheticEvent, useEffect, useState} from "react";
import Loader from "@/components/loader/Loader";
import {ConfigType} from "@/types/configTypes";
import {getConfig, setConfig} from "@/api/configApi";
import {Alert, Button, Snackbar, SnackbarCloseReason, Stack, TextField} from "@mui/material";

const Config = () => {
    const [isLoading, setIsLoading] = useState(true)

    const [cfg, setCfg] = useState("")


    const [edit, setEdit] = useState(false)

    const [open, setOpen] = useState(false)


    useEffect(() => {
        getConfig().then((data) => {
            setCfg(data.data)
        }).catch((err) => {
            console.log(err)
        }).finally(() => {
            setIsLoading(false)
        })
    }, [])


    const handleClick = () => {
        setOpen(true);
    };


    let isCorrect = true

    try {
        const _ = JSON.parse(cfg) as ConfigType
    } catch (e) {
        isCorrect = false
    }

    if (isLoading) {
        return <Loader/>
    }

    return (<Stack height={"100%"} width={"100%"} spacing={3}>
        <Button disabled={!isCorrect} variant={"outlined"} sx={{width: "200px"}} onClick={() => {
            if (edit) {

                setConfig(JSON.parse(cfg) as ConfigType).then((data) => {
                    setOpen(true)
                }).catch((err) => {
                    console.log(err)
                })
            }

            setEdit(!edit)
        }}>
            {edit ? "Сохранить" : "Редактировать"}
        </Button>

        <TextField multiline={true} rows={"40"} value={cfg} error={!isCorrect}
                   onChange={(e) => setCfg(e.target.value)} disabled={!edit}/>


        <Snackbar open={open} autoHideDuration={2000} onClose={() => {
            setOpen(false)
        }}>
            <Alert onClose={() => {
                setOpen(false)
            }} severity="success">
                Конфигурация успешно обновлена
            </Alert>
        </Snackbar>
    </Stack>)
}


export default Config