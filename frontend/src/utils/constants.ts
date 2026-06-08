export interface Option {
  value: string;
  label: string;
  emoji?: string;
}

export const RELATION_GROUPS: Option[] = [
  { value: "relative", label: "亲戚", emoji: "🏮" },
  { value: "friend", label: "朋友", emoji: "🤝" },
  { value: "colleague", label: "同事", emoji: "💼" },
  { value: "family", label: "家人", emoji: "🏠" },
  { value: "other", label: "其他", emoji: "✨" },
];

export const CHANNELS: Option[] = [
  { value: "cash", label: "现金", emoji: "💵" },
  { value: "wechat", label: "微信", emoji: "🟢" },
  { value: "alipay", label: "支付宝", emoji: "🔵" },
];

export const DIRECTIONS: Option[] = [
  { value: "received", label: "收礼" },
  { value: "given", label: "随礼" },
];

export const REMINDER_KINDS: Option[] = [
  { value: "birthday", label: "生日", emoji: "🎂" },
  { value: "festival", label: "节日", emoji: "🎉" },
  { value: "event", label: "喜事", emoji: "🎊" },
];

export const BLESSING_SCENES: Option[] = [
  { value: "thanks_wedding", label: "婚礼答谢" },
  { value: "thanks_moments", label: "朋友圈答谢" },
  { value: "birthday", label: "生日祝福" },
  { value: "festival", label: "节日祝福" },
  { value: "return_gift", label: "回礼答谢" },
];

export function labelOf(options: Option[], value: string): string {
  return options.find((o) => o.value === value)?.label || value;
}

export function emojiOf(options: Option[], value: string): string {
  return options.find((o) => o.value === value)?.emoji || "";
}
