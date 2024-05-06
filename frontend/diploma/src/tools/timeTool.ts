export const timestampToDate = (props: number) => {
    const n = Number(props) * 1000
    const dt = new Date(n)

    return dt.toLocaleTimeString()
}