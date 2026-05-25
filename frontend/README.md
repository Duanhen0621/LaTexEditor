# AI Frontend

这是一个基于 Vue 3 + Vite 的前端项目，用于和 `ai_service` 做联动，提供三栏工作区：Markdown 编辑、实时预览、聊天与操作面板。

## 功能

- Markdown 编辑与实时预览
- 图片 OCR 识别
- 语音录制与转写
- 文本 Chat 对话
- 历史消息流展示
- 草稿保存与历史记录查看

## 本地运行

1. 安装依赖

```bash
cd frontend
npm install
```

2. 启动开发服务器

```bash
npm run dev
```

默认前端会请求 `http://localhost:8001`，如果你的 AI 服务运行在别的地址，可以在 `.env` 中设置：

```env
VITE_API_BASE=http://localhost:8001
```

## 与 AI 服务层的对接

当前前端调用的是 `ai_service` 提供的三个接口，且都使用 `FormData` 发送：

- `POST /api/v1/ai/ocr`
  - 字段：`file`
- `POST /api/v1/ai/speech`
  - 字段：`file`、`language`
- `POST /api/v1/ai/chat`
  - 字段：`message`

前端会先检查返回 JSON 中的 `code`：

- `code === 0` 表示成功
- 其他值表示失败，错误信息会显示在聊天历史区域

### 数据流

- 图片识别成功后，读取 `res.info`
- 语音转写成功后，读取 `res.text` 并拼接到输入框
- 文本对话成功后，读取 `res.reply`

## 目录结构

```text
src/
├─ App.vue
├─ main.ts
├─ components/
│  ├─ EditorPanel.vue
│  ├─ InteractionPanel.vue
│  └─ PreviewPanel.vue
├─ composables/
│  └─ useRecorder.ts
├─ lib/
│  └─ apiClient.ts
├─ pages/
│  ├─ Main.vue
│  └─ HistoryPage.vue
├─ store/
│  └─ useAppStore.ts
├─ styles.css
└─ index.css
```

## 说明

- 录音最长 60 秒
- 聊天历史是消息流
- 语音转写结果会自动拼接到消息输入框末尾
- 所有请求都通过 `FormData` 发送，浏览器会自动设置 `multipart/form-data`
