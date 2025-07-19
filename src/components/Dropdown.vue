<script setup>
defineProps({
  label: String,
  options: Array,
  modelValue: String,
});
defineEmits(['update:modelValue']);
</script>

<template>
  <div class="column is-narrow">
    <label class="label has-text-white" style="font-family: Inter;">{{ label }}</label>
    <div class="select is-dark">
      <select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)">
        <option v-for="item in options" :key="item" :value="item">{{ item }}</option>
      </select>
    </div>
  </div>
</template>
