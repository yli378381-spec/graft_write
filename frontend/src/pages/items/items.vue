<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { api } from "@/utils/request";
import { RELATION_GROUPS, labelOf } from "@/utils/constants";
import { fmtDate } from "@/utils/format";
import type { GiftItem } from "@/types";

const items = ref<GiftItem[]>([]);
const showForm = ref(false);
const guest_name = ref("");
const item_name = ref("");
const quantity = ref<string>("1");
const relation_group = ref("relative");
const note = ref("");

async function load() {
  try {
    items.value = await api.get<GiftItem[]>("/api/items");
  } catch (e: any) {
    uni.showToast({ title: e.message || "加载失败", icon: "none" });
  }
}

async function add() {
  if (!guest_name.value.trim() || !item_name.value.trim()) {
    uni.showToast({ title: "请填写姓名和礼品名称", icon: "none" });
    return;
  }
  try {
    await api.post("/api/items", {
      guest_name: guest_name.value.trim(),
      item_name: item_name.value.trim(),
      quantity: Number(quantity.value) || 1,
      relation_group: relation_group.value,
      note: note.value || null,
    });
    guest_name.value = "";
    item_name.value = "";
    quantity.value = "1";
    note.value = "";
    showForm.value = false;
    uni.showToast({ title: "已登记", icon: "success" });
    load();
  } catch (e: any) {
    uni.showToast({ title: e.message || "登记失败", icon: "none" });
  }
}

async function remove(it: GiftItem) {
  const res = await uni.showModal({ title: "删除", content: `删除「${it.item_name}」？` });
  if (!(res as any).confirm) return;
  await api.del(`/api/items/${it.id}`);
  load();
}

onShow(() => load());
</script>

<template>
  <view class="wrap">
    <view class="hint lx-card">
      <text class="lx-muted">实物礼以文字记录礼品名称、赠送人与数量。（拍照识别、智能估价为升级版功能）</text>
    </view>

    <button class="lx-btn lx-btn-block" @tap="showForm = !showForm">
      {{ showForm ? "收起" : "＋ 登记一件实物礼" }}
    </button>

    <view v-if="showForm" class="lx-card form">
      <view class="field">
        <text class="label">赠送人</text>
        <input class="input" v-model="guest_name" placeholder="如：李姐" />
      </view>
      <view class="field">
        <text class="label">礼品名称</text>
        <input class="input" v-model="item_name" placeholder="如：四件套 / 茶具 / 红酒" />
      </view>
      <view class="field">
        <text class="label">数量</text>
        <input class="input" v-model="quantity" type="number" placeholder="1" />
      </view>
      <view class="field">
        <text class="label">关系分组</text>
        <view class="opts">
          <view
            v-for="g in RELATION_GROUPS" :key="g.value"
            class="lx-chip" :class="{ active: relation_group === g.value }"
            @tap="relation_group = g.value"
          >{{ g.emoji }} {{ g.label }}</view>
        </view>
      </view>
      <view class="field">
        <text class="label">备注 (选填)</text>
        <input class="input" v-model="note" placeholder="颜色 / 品牌 / 心意" />
      </view>
      <button class="lx-btn lx-btn-block" @tap="add">保存登记</button>
    </view>

    <view v-if="!items.length" class="lx-empty">还没有实物礼记录 🎁</view>

    <view class="item" v-for="it in items" :key="it.id">
      <view class="item-icon">🎁</view>
      <view class="item-main">
        <view class="lx-between">
          <text class="item-name">{{ it.item_name }} ×{{ it.quantity }}</text>
          <text class="del-x" @tap="remove(it)">删除</text>
        </view>
        <text class="lx-muted">{{ it.guest_name }} · {{ labelOf(RELATION_GROUPS, it.relation_group) }} · {{ fmtDate(it.recorded_at) }}</text>
        <text v-if="it.note" class="item-note">{{ it.note }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.wrap { padding: 28rpx 32rpx 60rpx; }
.hint { margin-bottom: 20rpx; }
.form { margin-top: 20rpx; display: flex; flex-direction: column; gap: 24rpx; }
.field { display: flex; flex-direction: column; gap: 14rpx; }
.label { font-size: 26rpx; color: var(--ink-2); }
.input { background: #f7f3ee; border-radius: 14rpx; padding: 22rpx 24rpx; font-size: 30rpx; }
.opts { display: flex; flex-wrap: wrap; gap: 14rpx; }
.opts .lx-chip { margin-right: 0; }

.item {
  display: flex; gap: 20rpx; background: var(--card); border-radius: 20rpx;
  padding: 24rpx; margin-top: 18rpx; box-shadow: 0 6rpx 24rpx rgba(168,23,40,0.05);
}
.item-icon { font-size: 44rpx; }
.item-main { flex: 1; display: flex; flex-direction: column; gap: 8rpx; }
.item-name { font-size: 30rpx; font-weight: 600; }
.item-note { font-size: 24rpx; color: var(--ink-2); }
.del-x { font-size: 22rpx; color: var(--ink-2); }
</style>
