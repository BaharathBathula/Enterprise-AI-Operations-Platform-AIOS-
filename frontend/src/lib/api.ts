const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1";


export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(
    status: number,
    detail: string,
  ) {
    super(detail);

    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}


type ApiRequestOptions = RequestInit & {
  token?: string;
};


export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const {
    token,
    headers,
    ...requestOptions
  } = options;

  const requestHeaders =
    new Headers(headers);

  if (
    requestOptions.body &&
    !(requestOptions.body instanceof FormData) &&
    !requestHeaders.has("Content-Type")
  ) {
    requestHeaders.set(
      "Content-Type",
      "application/json",
    );
  }

  if (token) {
    requestHeaders.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  const response = await fetch(
    `${API_URL}${path}`,
    {
      ...requestOptions,
      headers: requestHeaders,
    },
  );

  if (!response.ok) {
    let detail =
      "API request failed";

    try {
      const body =
        await response.json();

      if (
        typeof body.detail ===
        "string"
      ) {
        detail = body.detail;
      }
    } catch {
      detail =
        response.statusText ||
        detail;
    }

    throw new ApiError(
      response.status,
      detail,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (
    await response.json()
  ) as T;
}