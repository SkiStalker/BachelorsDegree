import {
    CircularProgress,
    FormControl, IconButton,
    InputLabel,
    MenuItem, Paper,
    Select,
    Stack, styled,
    Table, TableBody, TableCell, tableCellClasses,
    TableContainer, TableFooter, TableHead, TablePagination, TableRow,
    TextField,
    Typography
} from "@mui/material";
import {useEffect, useState} from "react";
import {AutoDataType} from "@/types/autoDataTypes";
import TablePaginationActions from "@mui/material/TablePagination/TablePaginationActions";
import CloseIcon from "@mui/icons-material/Close";
import {getAutoInfo} from "@/api/dataAutoApi";

const StyledTableCell = styled(TableCell)(({theme}) => ({

    alignSelf: "left",
}));


const DataPanel = () => {
    const [filterField, setFilterField] = useState<string>("")

    const [filterValue, setFilterValue] = useState<string>("")

    const [orderField, setOrderField] = useState<string>("created_at")

    const [orderDirection, setOrderDirection] = useState<string>("desc")

    const [page, setPage] = useState<number>(0)

    const [rowsPerPage, setRowsPerPage] = useState<number>(10)

    const [data, setData] = useState<AutoDataType[]>([])

    const [completedFilterValue, setCompletedFilterValue] = useState<string>("")

    const [filterValueTimer, setFilterValueTimer] = useState<NodeJS.Timeout | undefined>(undefined)

    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        setIsLoading(true)

        getAutoInfo({
            limit: rowsPerPage,
            offset: page * rowsPerPage,
            filter_field: (filterField && completedFilterValue) ? filterField : undefined,
            filter_value: (filterField && completedFilterValue) ? completedFilterValue : undefined,
            order_direction: orderDirection,
            order_field: orderField,
        }).then((data) => {
            setData(data.data.data)

            setIsLoading(false)
        }).catch((err) => {
            console.log(err)
        })

    }, [page, rowsPerPage, filterField, completedFilterValue, orderDirection, orderField]);

    return (<Stack spacing={3} sx={{height: "70vh"}}>
        <Stack direction={"row"} spacing={3}>
            <Typography sx={{alignSelf: "center"}}>Фильтр</Typography>
            <FormControl sx={{minWidth: "300px"}}>
                <InputLabel sx={{display: filterField ? "none" : undefined}}>
                    Выберите поле для фильтрации
                </InputLabel>
                <Select
                    value={filterField}
                    onChange={(ev) => {
                        setFilterField(ev.target.value)
                    }}
                >
                    <MenuItem value="id">ID</MenuItem>
                    <MenuItem value="auto_id">ID Авто</MenuItem>
                    <MenuItem value="driver_id">ID Водителя</MenuItem>
                    <MenuItem value="fuel">Уровень топлива</MenuItem>
                    <MenuItem value="balance">Баланс топливной карты</MenuItem>
                    <MenuItem value="velocity">Скорость</MenuItem>
                    <MenuItem value="positionx">Долгота</MenuItem>
                    <MenuItem value="positiony">Широта</MenuItem>
                    <MenuItem value="created_at">Дата создания</MenuItem>
                </Select>

            </FormControl>


            <TextField sx={{minWidth: "250px"}} placeholder={"Введите занчение фильтра"} value={filterValue}
                       onChange={(ev) => {
                           setFilterValue(ev.target.value)

                           if (filterValueTimer != undefined) {
                               clearTimeout(filterValueTimer)
                           }

                           setFilterValueTimer(setTimeout(() => {
                               setCompletedFilterValue(ev.target.value)
                           }, 1000))


                       }}
                       error={filterValue == "" && filterField != ""}

            />


            <IconButton onClick={() => {
                setFilterField("")
                setFilterValue("")
                setPage(0)
            }}>
                <CloseIcon/>
            </IconButton>

        </Stack>

        <Stack direction={"row"} spacing={3}>
            <Typography sx={{alignSelf: "center"}}>Сортировка</Typography>
            <FormControl sx={{minWidth: "300px"}}>
                <InputLabel>
                    Выберите поле для сортировки
                </InputLabel>
                <Select
                    value={orderField}
                    onChange={(ev) => {
                        setOrderField(ev.target.value)
                        setPage(0)
                    }}
                >
                    <MenuItem value="id">ID</MenuItem>
                    <MenuItem value="auto_id">ID Авто</MenuItem>
                    <MenuItem value="driver_id">ID Водителя</MenuItem>
                    <MenuItem value="fuel">Уровень топлива</MenuItem>
                    <MenuItem value="balance">Баланс топливной карты</MenuItem>
                    <MenuItem value="velocity">Скорость</MenuItem>
                    <MenuItem value="positionx">Долгота</MenuItem>
                    <MenuItem value="positiony">Широта</MenuItem>
                    <MenuItem value="created_at">Дата создания</MenuItem>
                </Select>

            </FormControl>

            <FormControl sx={{minWidth: "200px"}}>
                <InputLabel>
                    Выберите порядок сортировки
                </InputLabel>
                <Select
                    value={orderDirection}

                    onChange={(ev) => {
                        setOrderDirection(ev.target.value)
                        setPage(0)
                    }}
                >

                    <MenuItem value="asc">По возрастанию</MenuItem>
                    <MenuItem value="desc">По убыванию</MenuItem>
                </Select>

            </FormControl>
        </Stack>


        {isLoading ? <CircularProgress/> :


            <TableContainer component={Paper} sx={{flexGrow: 1}}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <StyledTableCell>ID</StyledTableCell>
                            <StyledTableCell>ID Авто</StyledTableCell>
                            <StyledTableCell>ID Водителя</StyledTableCell>
                            <StyledTableCell>Уровень топлива</StyledTableCell>
                            <StyledTableCell>Баланс топливной карты</StyledTableCell>
                            <StyledTableCell>Скорость</StyledTableCell>
                            <StyledTableCell>Долгота</StyledTableCell>
                            <StyledTableCell>Широта</StyledTableCell>
                            <StyledTableCell>Дата создания</StyledTableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>

                        {data.map((item) => {
                            return (
                                <TableRow key={item.id}>
                                    <StyledTableCell>{item.id}</StyledTableCell>
                                    <StyledTableCell>{item.auto_id}</StyledTableCell>
                                    <StyledTableCell>{item.driver_id}</StyledTableCell>
                                    <StyledTableCell>{item.fuel}</StyledTableCell>
                                    <StyledTableCell>{item.balance}</StyledTableCell>
                                    <StyledTableCell>{item.velocity}</StyledTableCell>
                                    <StyledTableCell>{item.positionx}</StyledTableCell>
                                    <StyledTableCell>{item.positiony}</StyledTableCell>
                                    <StyledTableCell>{item.created_at}</StyledTableCell>
                                </TableRow>
                            )

                        })}


                    </TableBody>

                    <TableFooter>
                        <TableRow>
                            <TablePagination
                                count={data?.at(0)?.count || 0}
                                rowsPerPage={rowsPerPage}
                                rowsPerPageOptions={[5, 10, 20]}
                                page={page}
                                onPageChange={(e, new_page) => {
                                    setPage(new_page)
                                }}

                                onRowsPerPageChange={(e) => {
                                    setRowsPerPage(Number(e.target.value))
                                }}

                            />
                        </TableRow>
                    </TableFooter>

                </Table>


            </TableContainer>
        }

    </Stack>)
}

export default DataPanel;