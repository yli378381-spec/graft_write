// API base URL. Override at build time with VITE_API_BASE (H5) or edit here for mini program.
const fromEnv = (import.meta as any)?.env?.VITE_API_BASE as string | undefined;

export const API_BASE: string = fromEnv && fromEnv.length > 0 ? fromEnv : "http://localhost:8000";

export const BRAND = {
  name: "喜鹊礼簿",
  slogan: "记好每一份心意",
  mascot: "阿喜",
  mascotImg: "/static/ip/axi-mascot.svg",
};
