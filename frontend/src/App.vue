<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './store/auth'

const authStore = useAuthStore()

// 初始化认证状态
onMounted(async () => {
  await authStore.initAuth()
})
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
}
</style>