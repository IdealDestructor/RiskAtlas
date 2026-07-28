
export function getAddr(path) {
    if (process.env.NODE_ENV === 'development') {
        return `/api${path}`
    }
    return path
}
