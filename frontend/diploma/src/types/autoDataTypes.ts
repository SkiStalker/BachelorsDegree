export interface AutoDataType {
    id: number,
    count: number,
    auto_id: string,
    driver_id: string,
    positionx: number,
    positiony: number,
    fuel: number,
    balance: number,
    velocity: number
    created_at: string,
}


export interface AutoDataRequest {
    offset: number | undefined,
    limit: number | undefined,
    order_field: string | undefined,
    order_direction: string | undefined,
    filter_field: string | undefined,
    filter_value: string | undefined
}