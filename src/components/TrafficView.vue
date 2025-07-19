<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

import { AgGridVue } from "ag-grid-vue3";
import { themeQuartz, colorSchemeDark } from 'ag-grid-community'

const eventsMap = new Map() // Fast UID lookup
const eventsList = ref([])  // Only used for display in ag-Grid
const gridApi = ref(null)   // Store the ag-Grid API

const selected = ref(null)

const columnDefs = [
  { headerName: 'UID', field: 'uid', width: 170 },
  { headerName: 'GOID', field: 'goid', width: 170 },
  { headerName: 'Timestamp', field: 'ts_ns', valueFormatter: ({ value }) => formatTimestamp(value), width: 130,},
  { headerName: 'Component', field: 'comm', width: 150 },
  { headerName: 'Node', field: 'node', width: 80 }, // <-- Added node column
  { headerName: 'Source → Destination', field: 'sourceAddrStr', width: 260 },
  { headerName: 'Ports', field: 'sourcePortStr', width: 150,},
  { headerName: 'Length', field: 'data_len', width: 100 },
]

function formatTimestamp(ns) {
  return new Date(ns / 1e6).toLocaleTimeString()
}

function addEvent(event) {
  if (eventsMap.has(event.uid)) return // O(1) check

  event.sourceAddrStr = (event.normalized_addr_info?.srcIP || '-') + ' → ' + (event.normalized_addr_info?.dstIP || '-')
  event.sourcePortStr = (event.normalized_addr_info?.srcPort || '-') + ' → ' + (event.normalized_addr_info?.dstPort || '-')

  eventsMap.set(event.uid, event)

  // Push directly into ag-Grid without triggering a full re-render
  if (gridApi.value) {
    gridApi.value.applyTransaction({ add: [event] })
  } else {
    // Fallback: initial render population
    eventsList.value.push(event)
  }

  // Optionally limit size
  // if (eventsMap.size > 1000) {
  //   const oldest = eventsList.value.shift()
  //   eventsMap.delete(oldest.uid)
  //   gridApi.value?.applyTransaction({ remove: [oldest] })
  // }
}


let socket = null

function getWebSocketUrl() {
  const loc = window.location;
  const protocol = loc.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${loc.host}/ws`;
}


function setupWebSocket() {
  const webSockPath = getWebSocketUrl();
  // const webSockPath = "ws://192.168.100.3:8085/ws"
  socket = new WebSocket(webSockPath) // Adjust if different host

  socket.onopen = () => {
    console.log("WebSocket connection established.")
  }

  socket.onmessage = (msg) => {
    try {
      const event = JSON.parse(msg.data)
      if (event?.uid) {
        addEvent(event)
      }
    } catch (err) {
      console.error("Failed to parse WebSocket message:", err)
    }
  }

  socket.onclose = () => {
    console.warn("WebSocket connection closed.")
  }

  socket.onerror = (err) => {
    console.error("WebSocket error:", err)
  }
}

onMounted(() => {
  setupWebSocket()
  setInterval(
    () => {
      if (socket && socket.readyState === WebSocket.CLOSED) {
        console.warn("WebSocket is closed, attempting to reconnect...")
        setupWebSocket()
      }
    }, 5000) // Check every 5 seconds
}
);

onBeforeUnmount(() => {
  if (socket) socket.close()
})


function onRowClicked(event) {
  selected.value = event.data
}

const getRowId = (params) => params.data.uid.toString()

import { computed } from 'vue'

const decodedAddrInfo = computed(() => {
  return selected.value?.normalized_addr_info != null ? 
    {
      src: selected.value.normalized_addr_info.srcIP,
      dst: selected.value.normalized_addr_info.dstIP,
      srcPort: selected.value.normalized_addr_info.srcPort,
      dstPort: selected.value.normalized_addr_info.dstPort
    } : 
    { src: 'N/A', dst: 'N/A', srcPort: 'N/A', dstPort: 'N/A' }
})

const http2info = computed(() => {
  if (!selected.value?.frames || selected.value.frames.length < 1) return 'No HTTP2 frames found';
  return selected.value.frames
    .map(frame => {return frame.additional_info})
    .join('\n\n');
});

const gzipData = computed(() => {
  if (!selected.value?.frames || selected.value.frames.length < 1) return null;
  const gzipFrames = selected.value.frames.filter(frame => frame.is_gzip);
  if (gzipFrames.length === 0) return null;
  return gzipFrames.map(frame => frame.gzip_data).join('\n\n');
});

const displayFormat = ref('hex') // Default to hex format

const formattedData = computed(() => {
  if (!selected.value?.data) return ''
  const base64 = selected.value.data
  const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0))

  const bytesPerLine = 26

  if (displayFormat.value === 'hex') {
    return bytes
      .reduce((lines, byte, i) => {
        const hex = byte.toString(16).padStart(2, '0')
        const lineIndex = Math.floor(i / bytesPerLine)
        if (!lines[lineIndex]) lines[lineIndex] = []
        lines[lineIndex].push(hex)
        return lines
      }, [])
      .map(line => line.join(' '))
      .join('\n')
  }

  if (displayFormat.value === 'binary') {
    return bytes
      .reduce((lines, byte, i) => {
        const bin = byte.toString(2).padStart(8, '0')
        const lineIndex = Math.floor(i / 8)
        if (!lines[lineIndex]) lines[lineIndex] = []
        lines[lineIndex].push(bin)
        return lines
      }, [])
      .map(line => line.join(' '))
      .join('\n')
  }

  if (displayFormat.value === 'ascii') {
    let textDecoder = new TextDecoder('ascii')
    try {
      return (textDecoder.decode(bytes))
    } catch (e) {
      console.error("Failed to decode ASCII:", e)
      return 'Invalid ASCII data'
    }
  }

    if (displayFormat.value === 'utf8') {
    let textDecoder = new TextDecoder('utf-8')
    try {
      return (textDecoder.decode(bytes))
    } catch (e) {
      console.error("Failed to decode UTF-8:", e)
      return 'Invalid UTF-8 data'
    }
  }

  return base64
})

const rowSelection = {
    mode: null,
};

const theme = themeQuartz.withPart(colorSchemeDark);

function onGridReady(params) {
  gridApi.value = params.api
}
</script>

<style scoped>
.traffic-grid {
  border: 2px solid #00d1b2;
  border-radius: 5px;
  font-family: monospace;
}

.detail-label {
  color: #00d1b2;
  font-weight: 500;
}

.detail-value {
  color: #e0e0e0;
}

.detail-muted {
  color: #999;
  font-size: 0.85em;
}
</style>

<template>
  <div class="fixed-grid has-3-cols">
    <div class="p-4 grid">
      <!-- Traffic Table -->
      <div class="cell is-col-span-2">
        <p class="title is-4 has-text-white" style="font-family: Inter;">Traffic</p>
        <ag-grid-vue class="ag-theme-alpine-dark traffic-grid" :theme="theme" style="height: 70vh; width: 100%;"
          :columnDefs="columnDefs" :rowData="eventsList" :rowSelection="rowSelection" @rowClicked="onRowClicked" @grid-ready="onGridReady"
          :getRowId="getRowId" />
      </div>

      <!-- Details Panel -->
      <div class="cell">
        <p class="title is-4 has-text-white" style="font-family: Inter;">Details</p>
        <div style="
          border: 2px solid #00d1b2; 
          background-color: #1a1a1a; 
          height: 70vh; 
          border-radius: 5px; 
          padding: 10px; 
          color: white;    
          overflow-wrap: break-word;
          word-break: break-all;
          white-space: normal;
          overflow-y: auto;
        ">
          <div v-if="selected">
            <p><span class="detail-label">ID:</span> <span class="detail-value">{{ selected.uid }}</span></p>
            <p><span class="detail-label">GOID:</span> <span class="detail-value">{{ selected.goid }}</span></p>
            <p>
              <span class="detail-label">Timestamp: </span>
              <span class="detail-value">{{ formatTimestamp(selected.ts_ns) }}</span>
            </p>
            <p><span class="detail-label">Component: </span> <span class="detail-value">{{ selected.comm }}</span></p>
            <p>
              <span class="detail-label">Source → Destination: </span>
              <span class="detail-value">{{ decodedAddrInfo.src }} → {{ decodedAddrInfo.dst }}</span>
            </p>
            <p>
              <span class="detail-label">Ports: </span>
              <span class="detail-value">{{ decodedAddrInfo.srcPort }} → {{ decodedAddrInfo.dstPort }}</span>
            </p>
            <p>
              <span class="detail-label">Data Length: </span>
              <span class="detail-value">{{ selected.data_len }}</span>
              <span class="detail-muted"> bytes</span>
            </p>

            <p>
              <span class="detail-label">Protocol: </span>
              <span class="detail-value">{{ selected.frames != null ? "HTTP2":"Unknown"  }}</span>
            </p>

            <div v-if="http2info && selected.frames != null">
              <p><strong>HTTP2: </strong></p>
              <pre style="font-size: small; white-space: pre-wrap; word-break: break-all;">{{ http2info }}</pre>
            </div>

            <div v-if="gzipData && gzipData.length">
              <p style="margin-bottom: 0.5rem; margin-top: 7px;"><strong>GZIP: </strong></p>
              <pre style="font-size: small; white-space: pre-wrap; word-break: break-all;">
{{ gzipData }}
              </pre>
            </div>

            <div style="margin-bottom: 0.5rem;margin-top: 0.6rem;">
              <label>Display format:</label>
              <div style="margin-left: 0.5rem;" class="select is-small is-dark">
                <select v-model="displayFormat">
                  <option value="base64">Base64</option>
                  <option value="hex">Hex</option>
                  <option value="binary">Binary</option>
                  <option value="ascii">ASCII</option>
                  <option value="utf8">UTF-8</option>
                </select>
              </div>
            </div>

            <p style="margin-bottom: 0.5rem; margin-top: 7px;"><strong>Data:</strong></p>
            <!-- <span style="font-size: small;  word-break: break-word;">{{ formattedData }}</span> -->
            <pre style="font-size: small; white-space: pre-wrap; word-break: break-all;">
{{ formattedData }}
            </pre>
          </div>
          <div v-else>
            <p>Select a row to view details.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
