import { API_BASE } from "@/config";

export interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  data?: Record<string, any>;
  query?: Record<string, any>;
}

function buildUrl(path: string, query?: Record<string, any>): string {
  let url = API_BASE + path;
  if (query) {
    const parts: string[] = [];
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null && v !== "") {
        parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`);
      }
    }
    if (parts.length) url += (url.includes("?") ? "&" : "?") + parts.join("&");
  }
  return url;
}

export function request<T = any>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", data, query } = options;
  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: buildUrl(path, query),
      method,
      data,
      header: { "Content-Type": "application/json" },
      success: (res) => {
        const status = res.statusCode || 0;
        if (status >= 200 && status < 300) {
          resolve(res.data as T);
        } else {
          const detail = (res.data as any)?.detail || "请求失败";
          reject(new Error(typeof detail === "string" ? detail : JSON.stringify(detail)));
        }
      },
      fail: (err) => reject(new Error(err.errMsg || "网络错误")),
    });
  });
}

export const api = {
  get: <T = any>(path: string, query?: Record<string, any>) => request<T>(path, { method: "GET", query }),
  post: <T = any>(path: string, data?: Record<string, any>) => request<T>(path, { method: "POST", data }),
  put: <T = any>(path: string, data?: Record<string, any>) => request<T>(path, { method: "PUT", data }),
  del: <T = any>(path: string) => request<T>(path, { method: "DELETE" }),
};
