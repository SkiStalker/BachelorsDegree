export const merge = <T>(a: Array<T>, b: Array<T>, predicate = (a: T, b: T) => a === b) => {
    const c = [...a]
    b.forEach((bItem) => (c.some((cItem) => predicate(bItem, cItem)) ? null : c.push(bItem)))
    return c
}