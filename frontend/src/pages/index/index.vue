<script setup lang="ts">
import { ref } from "vue";
import { onShow, onPullDownRefresh } from "@dcloudio/uni-app";
import { api } from "@/utils/request";
import { BRAND } from "@/config";
import { RELATION_GROUPS, CHANNELS, labelOf, emojiOf } from "@/utils/constants";
import { money, fmtDate } from "@/utils/format";
import type { Gift, Stats } from "@/types";

const stats = ref<Stats | null>(null);
const gifts = ref<Gift[]>([]);
const group = ref<string>("");
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    const [s, g] = await Promise.all([
      api.get<Stats>("/api/stats"),
      api.get<Gift[]>("/api/gifts", { group: group.value, direction: "received" }),
    ]);
    stats.value = s;
    gifts.value = g;
  } catch (e: any) {
    uni.showToast({ title: e.message || "加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function pickGroup(v: string) {
  group.value = group.value === v ? "" : v;
  load();
}

function goAdd() {
  uni.navigateTo({ url: "/pages/add/add" });
}
function goItems() {
  uni.navigateTo({ url: "/pages/items/items" });
}
function goRemind() {
  uni.switchTab({ url: "/pages/remind/remind" });
}
function goStats() {
  uni.switchTab({ url: "/pages/stats/stats" });
}
function editGift(g: Gift) {
  uni.navigateTo({ url: `/pages/add/add?id=${g.id}` });
}

const channelTotal = (ch: string) => stats.value?.by_channel.find((c) => c.channel === ch)?.total || 0;

onShow(() => load());
onPullDownRefresh(async () => {
  await load();
  uni.stopPullDownRefresh();
});
</script>

<template>
  <view class="page">
    <!-- Hero header -->
    <view class="hero">
      <view class="hero-top">
        <view>
          <text class="hero-brand">{{ BRAND.name }}</text>
          <text class="hero-slogan">{{ BRAND.slogan }}</text>
        </view>
        <image class="hero-mascot" :src="BRAND.mascotImg" mode="aspectFit" />
      </view>

      <view class="total-card">
        <text class="total-label">收礼总额 (元)</text>
        <text class="total-value">¥ {{ money(stats?.total_amount) }}</text>
        <view class="total-sub">
          <text>共 {{ stats?.total_count || 0 }} 笔礼金</text>
          <text class="dot">·</text>
          <text>{{ stats?.item_count || 0 }} 件实物</text>
        </view>
        <view class="chan-row">
          <view class="chan" v-for="c in CHANNELS" :key="c.value">
            <text class="chan-label">{{ c.emoji }} {{ c.label }}</text>
            <text class="chan-amt">¥{{ money(channelTotal(c.value)) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Quick entries -->
    <view class="quick">
      <view class="quick-item" @tap="goAdd">
        <text class="quick-emoji">📝</text><text class="quick-text">记一笔</text>
      </view>
      <view class="quick-item" @tap="goItems">
        <text class="quick-emoji">🎁</text><text class="quick-text">实物礼</text>
      </view>
      <view class="quick-item" @tap="goRemind">
        <text class="quick-emoji">🔔</text><text class="quick-text">提醒祝福</text>
      </view>
      <view class="quick-item" @tap="goStats">
        <text class="quick-emoji">📊</text><text class="quick-text">看统计</text>
      </view>
    </view>

    <!-- Filter -->
    <scroll-view class="filter" scroll-x>
      <view class="lx-chip" :class="{ active: group === '' }" @tap="pickGroup('')">全部</view>
      <view
        class="lx-chip"
        :class="{ active: group === g.value }"
        v-for="g in RELATION_GROUPS"
        :key="g.value"
        @tap="pickGroup(g.value)"
      >{{ g.label }}</view>
    </scroll-view>

    <!-- Gift list -->
    <view class="list">
      <view class="lx-between list-head">
        <text class="lx-title">收礼明细</text>
        <text class="lx-muted">{{ gifts.length }} 笔</text>
      </view>

      <view v-if="!gifts.length" class="lx-empty">
        还没有记录，点右下角「+」记下第一份心意吧 🧧
      </view>

      <view class="gift" v-for="g in gifts" :key="g.id" @tap="editGift(g)">
        <view class="avatar">{{ (g.guest_name || "?").slice(0, 1) }}</view>
        <view class="gift-main">
          <view class="lx-between">
            <text class="gift-name">{{ g.guest_name }}</text>
            <text class="lx-amount">¥{{ money(g.amount) }}</text>
          </view>
          <view class="gift-meta">
            <text class="lx-tag">{{ labelOf(RELATION_GROUPS, g.relation_group) }}</text>
            <text class="gift-chan">{{ emojiOf(CHANNELS, g.channel) }} {{ labelOf(CHANNELS, g.channel) }}</text>
            <text class="gift-date">{{ fmtDate(g.recorded_at) }}</text>
          </view>
          <text v-if="g.note" class="gift-note">{{ g.note }}</text>
        </view>
      </view>
    </view>

    <!-- FAB -->
    <view class="fab" @tap="goAdd">
      <text class="fab-plus">＋</text>
    </view>
  </view>
</template>

<style scoped>
.page { min-height: 100vh; padding-bottom: 160rpx; }

.hero {
  background: linear-gradient(160deg, #e0224a, #c8102e);
  padding: 88rpx 32rpx 36rpx;
  border-bottom-left-radius: 36rpx;
  border-bottom-right-radius: 36rpx;
}
.hero-top { display: flex; align-items: center; justify-content: space-between; }
.hero-brand { color: #fff; font-size: 40rpx; font-weight: 700; display: block; letter-spacing: 2rpx; }
.hero-slogan { color: rgba(255,255,255,0.85); font-size: 24rpx; margin-top: 6rpx; display: block; }
.hero-mascot { width: 120rpx; height: 120rpx; }

.total-card {
  margin-top: 24rpx;
  background: rgba(255,255,255,0.14);
  border-radius: 24rpx;
  padding: 28rpx;
}
.total-label { color: rgba(255,255,255,0.85); font-size: 24rpx; }
.total-value { color: #fff; font-size: 64rpx; font-weight: 800; display: block; margin: 6rpx 0; }
.total-sub { color: rgba(255,255,255,0.85); font-size: 24rpx; }
.total-sub .dot { margin: 0 12rpx; }
.chan-row { display: flex; margin-top: 22rpx; gap: 16rpx; }
.chan {
  flex: 1; background: rgba(255,255,255,0.16); border-radius: 16rpx;
  padding: 16rpx; display: flex; flex-direction: column; gap: 6rpx;
}
.chan-label { color: rgba(255,255,255,0.9); font-size: 22rpx; }
.chan-amt { color: #fff; font-size: 28rpx; font-weight: 700; }

.quick {
  display: flex; justify-content: space-between;
  margin: 28rpx 32rpx 0; background: var(--card); border-radius: 20rpx; padding: 28rpx 12rpx;
  box-shadow: 0 6rpx 24rpx rgba(168, 23, 40, 0.06);
}
.quick-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 10rpx; }
.quick-emoji { font-size: 44rpx; }
.quick-text { font-size: 24rpx; color: var(--ink-2); }

.filter { white-space: nowrap; padding: 28rpx 32rpx 8rpx; }

.list { padding: 8rpx 32rpx; }
.list-head { margin-bottom: 12rpx; }
.gift {
  display: flex; gap: 20rpx; background: var(--card); border-radius: 20rpx;
  padding: 24rpx; margin-bottom: 18rpx; box-shadow: 0 6rpx 24rpx rgba(168, 23, 40, 0.05);
}
.avatar {
  width: 76rpx; height: 76rpx; border-radius: 50%; background: var(--brand-soft);
  color: var(--brand); display: flex; align-items: center; justify-content: center;
  font-size: 32rpx; font-weight: 700; flex-shrink: 0;
}
.gift-main { flex: 1; }
.gift-name { font-size: 30rpx; font-weight: 600; }
.gift-meta { display: flex; align-items: center; gap: 16rpx; margin-top: 10rpx; }
.gift-chan { font-size: 24rpx; color: var(--ink-2); }
.gift-date { font-size: 24rpx; color: var(--ink-2); }
.gift-note { font-size: 24rpx; color: var(--ink-2); margin-top: 10rpx; display: block; }

.fab {
  position: fixed; right: 40rpx; bottom: 60rpx; width: 110rpx; height: 110rpx;
  border-radius: 50%; background: linear-gradient(160deg, #e0224a, #c8102e);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 12rpx 28rpx rgba(200, 16, 46, 0.4);
}
.fab-plus { color: #fff; font-size: 60rpx; line-height: 1; margin-top: -6rpx; }
</style>
