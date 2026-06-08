export interface Gift {
  id: number;
  guest_name: string;
  relation_group: string;
  relation_detail?: string | null;
  channel: string;
  amount: number;
  direction: string;
  event_name?: string | null;
  note?: string | null;
  recorded_at: string;
  created_at: string;
}

export interface GiftItem {
  id: number;
  guest_name: string;
  relation_group: string;
  item_name: string;
  quantity: number;
  note?: string | null;
  recorded_at: string;
  created_at: string;
}

export interface Reminder {
  id: number;
  title: string;
  kind: string;
  remind_date: string;
  blessing_text?: string | null;
  done: number;
  created_at: string;
}

export interface ChannelStat {
  channel: string;
  total: number;
  count: number;
}
export interface GroupStat {
  relation_group: string;
  total: number;
  count: number;
}
export interface Stats {
  total_amount: number;
  total_count: number;
  item_count: number;
  received_amount: number;
  given_amount: number;
  by_channel: ChannelStat[];
  by_group: GroupStat[];
  max_gift?: Gift | null;
}

export interface BlessingTemplate {
  id: string;
  scene: string;
  relation: string;
  title: string;
  content: string;
}

export interface LockStatus {
  enabled: boolean;
  hint?: string | null;
}

export interface OkResult {
  ok: boolean;
  message?: string | null;
}

export interface DuplicateResult {
  duplicate: boolean;
  matches: Gift[];
}
