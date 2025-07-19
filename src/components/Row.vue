<!-- src/components/Row.vue -->
<template>
    <div class="row">
        <div class="col col-id">{{ source.id }}</div>
        <div class="col col-ts">{{ formatTimestamp(source.ts_ns) }}</div>
        <div class="col col-comm">{{ source.comm }}</div>
        <div class="col col-addr">{{ source.address_info.saddr4 }} → {{ source.address_info.daddr4 }}</div>
        <div class="col col-port">{{ source.address_info.sport }} → {{ source.address_info.dport }}</div>
        <div class="col col-len">{{ source.data_len }} bytes</div>
    </div>
</template>

<script setup>
defineProps({ source: Object })

function formatTimestamp(ns) {
  return new Date(ns / 1e6).toLocaleTimeString()
}
</script>

<style scoped>
.row {
  display: flex;
  padding: 5px;
  border-bottom: 1px solid #333;
  color: white;
}
</style>
