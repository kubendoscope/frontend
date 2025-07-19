<script setup>
import 'bulma/css/bulma.css';
import { ref } from 'vue';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community'; 

import Header from './components/Header.vue'
import NodeSelection from './components/NodeSelection.vue'
import TrafficView from './components/TrafficView.vue'

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);
</script>


<template>
  <section class="has-background-grey-darker min-vh-100">
    <Header />
    <NodeSelection />
    <TrafficView />
  </section>
</template>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}
</style>
