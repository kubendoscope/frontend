<script setup>
import Dropdown from './Dropdown.vue'
import { ref } from 'vue'

const nodes = ['cp01', 'cp02', "all-nodes"]
const components = ['kubeapiserver', 'kubelet', 'scheduler', "all-components"]

const selectedNode = ref('all-nodes')
const selectedComponent = ref('all-components')

defineExpose({
  selectedNode,
  selectedComponent
})
</script>

<template>
  <div class="columns is-vcentered p-4">
    <Dropdown label="Node" v-model="selectedNode" :options="nodes" />
    <Dropdown label="Component" v-model="selectedComponent" :options="components" />
  </div>
</template>
