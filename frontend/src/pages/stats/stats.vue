<script setup lang="ts">
import { ref, computed } from "vue";
import { onShow, onPullDownRefresh } from "@dcloudio/uni-app";
import { api } from "@/utils/request";
import { RELATION_GROUPS, CHANNELS, labelOf, emojiOf } from "@/utils/constants";
import { money } from "@/utils/format";
import type { Stats } from "@/types";

const stats = ref<Stats | null>(null);

async function load() {
  try {
    stats.value = await api.get<Stats>("/api/stats");
  } catch (e: any) {
    uni.showToast({ title: e.message || "加载失败", icon: "none" });
  }
}

const maxChannel = computed(() => {
  const arr = stats.value?.by_channel || [];
  return Math.max(1, ...arr.map((c) => c.total));
});
const maxGroup = computed(() => {
  const arr = stats.value?.by_group || [];
  return Math.max(1, ...arr.map((g) => g.total));
});

function pct(v: number, max: number) {
  return Math.max(4, Math.round((v / max) * 100));
}

function exportSummary() {
  const s = stats.value;
  if (!s) return;
  const lines = [
    "【喜鹊礼簿 · 收礼账单】",
    `收礼总额：¥${money(s.total_amount)}（${s.total_count} 笔）`,
    `实物礼：${s.item_count} 件`,
    "",
    "— 按渠道 —",
    ...s.by_channel.map((c) => `${labelOf(CHANNELS, c.channel)}：¥${money(c.total)}（${c.count}笔）`),
    "",
    "— 按关系 —",
    ...s.by_group.map((g) => `${labelOf(RELATION_GROUPS, g.relation_group)}：¥${money(g.total)}（${g.count}笔）`),
  ];
  uni.setClipboardData({
    data: lines.join("\n"),
    success: () => uni.showToast({ title: "账单已复制，可粘贴分享", icon: "none" }),
  });
}

onShow(() => load());
onPullDownRefresh(async () => {
  await load();
  uni.stopPullDownRefresh();
});
</script>

<template>
  <view class="wrap">
    <view class="overview">
      <view class="ov-card big">
        <text class="ov-label">收礼总额 (元)</text>
        <text class="ov-value">¥{{ money(stats?.total_amount) }}</text>
        <text class="ov-sub">共 {{ stats?.total_count || 0 }} 笔</text>
      </view>
      <view class="ov-col">
        <view class="ov-card">
          <text class="ov-label">收礼</text>
          <text class="ov-value sm">¥{{ money(stats?.received_amount) }}</text>
        </view>
        <view class="ov-card">
          <text class="ov-label">随礼</text>
          <text class="ov-value sm">¥{{ money(stats?.given_amount) }}</text>
        </view>
      </view>
    </view>

    <view class="lx-card section">
      <text class="lx-title">按支付渠道</text>
      <view class="bar-row" v-for="c in stats?.by_channel || []" :key="c.channel">
        <text class="bar-name">{{ emojiOf(CHANNELS, c.channel) }} {{ labelOf(CHANNELS, c.channel) }}</text>
        <view class="bar-track">
          <view class="bar-fill" :style="{ width: pct(c.total, maxChannel) + '%' }"></view>
        </view>
        <text class="bar-val">¥{{ money(c.total) }}</text>
      </view>
    </view>

    <view class="lx-card section">
      <text class="lx-title">按关系分组</text>
      <view v-if="!(stats?.by_group || []).length" class="lx-empty">暂无数据</view>
      <view class="bar-row" v-for="g in stats?.by_group || []" :key="g.relation_group">
        <text class="bar-name">{{ labelOf(RELATION_GROUPS, g.relation_group) }}</text>
        <view class="bar-track">
          <view class="bar-fill gold" :style="{ width: pct(g.total, maxGroup) + '%' }"></view>
        </view>
        <text class="bar-val">¥{{ money(g.total) }} · {{ g.count }}笔</text>
      </view>
    </view>

    <view class="lx-card section" v-if="stats?.max_gift">
      <text class="lx-title">最高的一份心意</text>
      <view class="top-gift">
        <view class="avatar">{{ (stats.max_gift.guest_name || '?').slice(0,1) }}</view>
        <view class="tg-main">
          <text class="tg-name">{{ stats.max_gift.guest_name }}</text>
          <text class="lx-muted">{{ labelOf(RELATION_GROUPS, stats.max_gift.relation_group) }}</text>
        </view>
        <text class="lx-amount big-amt">¥{{ money(stats.max_gift.amount) }}</text>
      </view>
    </view>

    <button class="lx-btn lx-btn-block lx-btn-ghost" @tap="exportSummary">复制账单摘要 · 一键分享</button>
    <view class="tip lx-muted">提示：复制后可粘贴到微信对话、备忘录，或配合系统截图保存账单。</view>
  </view>
</template>

<style scoped>
.wrap { padding: 28rpx 32rpx 60rpx; }
.overview { display: flex; gap: 20rpx; margin-bottom: 24rpx; }
.ov-card {
  background: var(--card); border-radius: 20rpx; padding: 28rpx;
  box-shadow: 0 6rpx 24rpx rgba(168, 23, 40, 0.06); display: flex; flex-direction: column; gap: 8rpx;
}
.ov-card.big {
  flex: 1.4; background: linear-gradient(160deg, #e0224a, #c8102e);
}
.ov-card.big .ov-label, .ov-card.big .ov-value, .ov-card.big .ov-sub { color: #fff; }
.ov-col { flex: 1; display: flex; flex-direction: column; gap: 20rpx; }
.ov-col .ov-card { flex: 1; }
.ov-label { font-size: 24rpx; color: var(--ink-2); }
.ov-value { font-size: 48rpx; font-weight: 800; color: var(--brand-deep); }
.ov-value.sm { font-size: 36rpx; }
.ov-sub { font-size: 24rpx; color: var(--ink-2); }

.section { margin-bottom: 24rpx; }
.section .lx-title { display: block; margin-bottom: 20rpx; }
.bar-row { display: flex; align-items: center; gap: 16rpx; margin-bottom: 20rpx; }
.bar-name { width: 150rpx; font-size: 26rpx; }
.bar-track { flex: 1; height: 22rpx; background: #f1eae3; border-radius: 999rpx; overflow: hidden; }
.bar-fill { height: 100%; background: linear-gradient(90deg, #e0224a, #c8102e); border-radius: 999rpx; }
.bar-fill.gold { background: linear-gradient(90deg, #e0b65b, #c9a14a); }
.bar-val { width: 200rpx; text-align: right; font-size: 24rpx; color: var(--ink-2); }

.top-gift { display: flex; align-items: center; gap: 20rpx; }
.avatar {
  width: 76rpx; height: 76rpx; border-radius: 50%; background: var(--brand-soft);
  color: var(--brand); display: flex; align-items: center; justify-content: center; font-weight: 700;
}
.tg-main { flex: 1; display: flex; flex-direction: column; gap: 6rpx; }
.tg-name { font-size: 30rpx; font-weight: 600; }
.big-amt { font-size: 40rpx; }
.tip { margin-top: 18rpx; display: block; text-align: center; }
</style>
