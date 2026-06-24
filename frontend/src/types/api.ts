export interface ApiResponse<T> {
    data: T;
    meta?: PaginationMeta;
}

export interface PaginationMeta {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
}

export interface ApiError {
    error: string;
    detail: string;
}