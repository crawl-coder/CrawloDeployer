<template>
  <div class="folder-upload-test">
    <h2>文件夹上传测试</h2>
    <el-upload
      v-model:file-list="fileList"
      :auto-upload="false"
      :multiple="true"
      :directory="true"
      :limit="5"
      @change="handleFileChange"
    >
      <el-button type="primary">选择文件/文件夹</el-button>
      <template #tip>
        <div class="el-upload__tip">
          支持上传ZIP包、Python脚本、文件夹或多个文件
        </div>
      </template>
    </el-upload>
    
    <div v-if="fileList.length > 0" class="file-list">
      <h3>选中的文件:</h3>
      <ul>
        <li v-for="(file, index) in fileList" :key="index">
          {{ file.name }} ({{ file.raw?.webkitRelativePath || '无路径信息' }})
        </li>
      </ul>
    </div>
    
    <el-button @click="handleUpload" type="success">上传文件</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { UploadUserFile } from 'element-plus'

const fileList = ref<UploadUserFile[]>([])

const handleFileChange = (uploadFile: any, uploadFiles: UploadUserFile[]) => {
  console.log('文件变化:', uploadFile, uploadFiles)
  fileList.value = uploadFiles
}

const handleUpload = () => {
  console.log('准备上传的文件列表:', fileList.value)
  fileList.value.forEach((file, index) => {
    console.log(`文件 ${index + 1}:`, {
      name: file.name,
      webkitRelativePath: file.raw?.webkitRelativePath,
      size: file.size,
      type: file.raw?.type
    })
  })
}
</script>

<style scoped>
.folder-upload-test {
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin: 20px;
}

.file-list {
  margin: 20px 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.file-list ul {
  list-style-type: none;
  padding: 0;
}

.file-list li {
  padding: 5px 0;
  border-bottom: 1px solid #ddd;
}
</style>