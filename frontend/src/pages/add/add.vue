<script setup lang="ts">
import { ref, computed } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { api } from "@/utils/request";
import { RELATION_GROUPS, CHANNELS, DIRECTIONS } from "@/utils/constants";
import { todayStr, money } from "@/utils/format";
import type { Gift, DuplicateResult } from "@/types";

const editId = ref<number | null>(null);
const guest_name = ref("");
const relation_group = ref("relative");
const relation_detail = ref("");
const channel = ref("cash");
const amount = ref<string>("");
const direction = ref("received");
const event_name = ref("");
const note = ref("");
const recorded_date = ref(todayStr());
const saving = ref(false);
const dupHint = ref("");

const isEdit = computed(() => editId.value !== null);
const presets = [200, 300, 500, 600, 800, 1000, 1314, 2000];

onLoad(async (q) => {
  if (q && q.id) {
    editId.value = Number(q.id);
    uni.setNavigationBarTitle({ title: "编辑记录" });
    try {
      const g = await api.get<Gift>(`/api/gifts/${editId.value}`);
      guest_name.value = g.guest_name;
      relation_group.value = g.relation_group;
      relation_detail.value = g.relation_detail || "";
      channel.value = g.channel;
      amount.value = String(g.amount);
      direction.value = g.direction;
      event_name.value = g.event_name || "";
      note.value = g.note || "";
      recorded_date.value = (g.recorded_at || "").slice(0, 10) || todayStr();
    } catch (e: any) {
      uni.showToast({ title: e.message || "加载失败", icon: "none" });
    }
  }
});

async function checkDup() {
  dupHint.value = "";
  if (isEdit.value || !guest_name.value.trim()) return;
  try {
    const r = await api.get<DuplicateResult>("/api/gifts/check-duplicate", {
      guest_name: guest_name.value.trim(),
      direction: direction.value,
    });
    if (r.duplicate && r.matches.length) {
      const m = r.matches[0];
      dupHint.value = `提醒：「${m.guest_name}」已记过 ¥${money(m.amount)}，确认不是重复录入哦`;
    }
  } catch (e) {
    // ignore
  }
}

function setPreset(v: number) {
  amount.value = String(v);
}

async function save() {
  if (!guest_name.value.trim()) {
    uni.showToast({ title: "请填写亲友姓名", icon: "none" });
    return;
  }
  const amt = Number(amount.value);
  if (isNaN(amt) || amt < 0) {
    uni.showToast({ title: "请填写正确金额", icon: "none" });
    return;
  }
  saving.value = true;
  const payload = {
    guest_name: guest_name.value.trim(),
    relation_group: relation_group.value,
    relation_detail: relation_detail.value || null,
    channel: channel.value,
    amount: amt,
    direction: direction.value,
    event_name: event_name.value || null,
    note: note.value || null,
    recorded_at: recorded_date.value + "T12:00:00",
  };
  try {
    if (isEdit.value) {
      await api.put(`/api/gifts/${editId.value}`, payload);
    } else {
      await api.post("/api/gifts", payload);
    }
    uni.showToast({ title: "已保存", icon: "success" });
    setTimeout(() => uni.navigateBack(), 500);
  } catch (e: any) {
    uni.showToast({ title: e.message || "保存失败", icon: "none" });
  } finally {
    saving.value = false;
  }
}

async function remove() {
  if (!isEdit.value) return;
  const res = await uni.showModal({ title: "删除记录", content: "确定删除这条礼金记录吗？" });
  if (!(res as any).confirm) return;
  try {
    await api.del(`/api/gifts/${editId.value}`);
    uni.showToast({ title: "已删除", icon: "success" });
    setTimeout(() => uni.navigateBack(), 500);
  } catch (e: any) {
    uni.showToast({ title: e.message || "删除失败", icon: "none" });
  }
}
</script>

<template>
  <view class="wrap">
    <!-- direction switch -->
    <view class="seg">
      <view
        v-for="d in DIRECTIONS"
        :key="d.value"
        class="seg-item"
        :class="{ active: direction === d.value }"
        @tap="direction = d.value; checkDup()"
      >{{ d.label }}</view>
    </view>

    <view class="lx-card form">
      <view class="field">
        <text class="label">亲友姓名</text>
        <input class="input" v-model="guest_name" placeholder="如：张伟" @blur="checkDup" />
      </view>
      <view v-if="dupHint" class="dup">{{ dupHint }}</view>

      <view class="field">
        <text class="label">关系分组</text>
        <view class="opts">
          <view
            v-for="g in RELATION_GROUPS"
            :key="g.value"
            class="lx-chip"
            :class="{ active: relation_group === g.value }"
            @tap="relation_group = g.value"
          >{{ g.emoji }} {{ g.label }}</view>
        </view>
      </view>

      <view class="field">
        <text class="label">金额 (元)</text>
        <input class="input amount-input" v-model="amount" type="digit" placeholder="0" />
        <view class="presets">
          <view v-for="p in presets" :key="p" class="preset" @tap="setPreset(p)">{{ p }}</view>
        </view>
      </view>

      <view class="field">
        <text class="label">支付渠道</text>
        <view class="opts">
          <view
            v-for="c in CHANNELS"
            :key="c.value"
            class="lx-chip"
            :class="{ active: channel === c.value }"
            @tap="channel = c.value"
          >{{ c.emoji }} {{ c.label }}</view>
        </view>
      </view>

      <view class="field">
        <text class="label">日期</text>
        <picker mode="date" :value="recorded_date" @change="(e:any) => recorded_date = e.detail.value">
          <view class="picker">{{ recorded_date }}</view>
        </picker>
      </view>

      <view class="field">
        <text class="label">事由 (选填)</text>
        <input class="input" v-model="event_name" placeholder="如：婚礼 / 满月 / 乔迁" />
      </view>

      <view class="field">
        <text class="label">备注 (选填)</text>
        <input class="input" v-model="relation_detail" placeholder="称呼/关系，如：大姨、发小" />
      </view>

      <view class="field">
        <text class="label">心意备注 (选填)</text>
        <textarea class="textarea" v-model="note" placeholder="记录这份心意背后的故事…" />
      </view>
    </view>

    <button class="lx-btn lx-btn-block save" :disabled="saving" @tap="save">
      {{ saving ? "保存中…" : (isEdit ? "保存修改" : "保存记录") }}
    </button>
    <button v-if="isEdit" class="lx-btn lx-btn-block lx-btn-ghost del" @tap="remove">删除记录</button>
  </view>
</template>

<style scoped>
.wrap { padding: 28rpx 32rpx 60rpx; }
.seg {
  display: flex; background: #f0e8e0; border-radius: 999rpx; padding: 6rpx; margin-bottom: 24rpx;
}
.seg-item { flex: 1; text-align: center; padding: 18rpx 0; border-radius: 999rpx; font-size: 28rpx; color: var(--ink-2); }
.seg-item.active { background: #fff; color: var(--brand); font-weight: 700; box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.06); }

.form { display: flex; flex-direction: column; gap: 28rpx; }
.field { display: flex; flex-direction: column; gap: 14rpx; }
.label { font-size: 26rpx; color: var(--ink-2); }
.input {
  background: #f7f3ee; border-radius: 14rpx; padding: 22rpx 24rpx; font-size: 30rpx;
}
.amount-input { font-size: 44rpx; font-weight: 700; color: var(--brand-deep); }
.textarea { background: #f7f3ee; border-radius: 14rpx; padding: 22rpx 24rpx; font-size: 28rpx; width: 100%; height: 140rpx; }
.opts { display: flex; flex-wrap: wrap; gap: 14rpx; }
.opts .lx-chip { margin-right: 0; margin-bottom: 6rpx; }
.picker { background: #f7f3ee; border-radius: 14rpx; padding: 22rpx 24rpx; font-size: 30rpx; }
.presets { display: flex; flex-wrap: wrap; gap: 14rpx; margin-top: 8rpx; }
.preset {
  background: var(--brand-soft); color: var(--brand); border-radius: 12rpx;
  padding: 12rpx 24rpx; font-size: 26rpx;
}
.dup {
  background: #fff7e6; color: #b9770a; border-radius: 12rpx; padding: 16rpx 20rpx;
  font-size: 24rpx; margin: -8rpx 0 4rpx;
}
.save { margin-top: 36rpx; }
.del { margin-top: 20rpx; }
</style>
