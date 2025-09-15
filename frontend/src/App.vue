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
  console.log('App.vue onMounted 开始初始化认证状态')
  try {
    await authStore.initAuth()
    console.log('App.vue 初始化完成，当前token:', authStore.token)
  } catch (error) {
    console.error('App.vue 初始化认证状态失败:', error)
  }
})
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
}
</style>