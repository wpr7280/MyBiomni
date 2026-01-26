# 客户端前端国际化实现指南

## 已完成的工作

### 1. 安装依赖
```bash
npm install i18next react-i18next
```

### 2. 创建的文件

- `src/i18n/index.ts` - i18n 配置文件
- `src/i18n/locales/zh-CN.json` - 中文翻译
- `src/i18n/locales/en-US.json` - 英文翻译
- `src/components/LanguageSwitcher.tsx` - 语言切换组件

### 3. 修改的文件

- `src/main.tsx` - 初始化 i18n，动态加载 Ant Design 语言包
- `src/components/Header.tsx` - 添加语言切换器和国际化文本

## 使用方法

### 在组件中使用翻译

```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('login.title')}</h1>
      <p>{t('login.subtitle')}</p>
    </div>
  );
}
```

### 带参数的翻译

```tsx
// 翻译文件中：
// "welcome": "Welcome, {{username}}!"

const { t } = useTranslation();
<p>{t('login.loginSuccess', { username: 'John' })}</p>
// 输出：Welcome, John!
```

## 需要继续完成的页面

以下页面需要添加国际化支持（使用 `useTranslation` hook）：

### 1. Login.tsx ✅ (Header 已完成)
- 需要替换所有硬编码的中文文本
- 使用 `t('login.xxx')` 替换

### 2. ChangePassword.tsx
- 需要替换所有硬编码的中文文本
- 使用 `t('changePassword.xxx')` 替换

### 3. Profile.tsx
- 需要替换所有硬编码的中文文本
- 使用 `t('profile.xxx')` 替换

### 4. ChatLayout.tsx
- 需要替换所有硬编码的中文文本
- 使用 `t('chat.xxx')` 替换

### 5. ChatWindow.tsx
- 需要替换所有硬编码的中文文本
- 使用 `t('chat.xxx')` 和 `t('execution.xxx')` 替换

### 6. ExecutionPanel.tsx
- 需要替换所有硬编码的中文文本
- 使用 `t('execution.xxx')` 替换

### 7. Footer.tsx
- 需要替换所有硬编码的中文文本
- 使用 `t('footer.xxx')` 替换

## 实现步骤（针对每个页面）

1. 在组件顶部导入 `useTranslation`：
```tsx
import { useTranslation } from 'react-i18next';
```

2. 在组件内部使用 hook：
```tsx
const { t } = useTranslation();
```

3. 替换所有硬编码文本：
```tsx
// 之前
<Button>登录</Button>

// 之后
<Button>{t('login.loginButton')}</Button>
```

4. 替换 message 提示：
```tsx
// 之前
message.success('登录成功');

// 之后
message.success(t('login.loginSuccess', { username: user.username }));
```

## 翻译文件结构

```json
{
  "common": {
    // 通用文本：按钮、操作等
  },
  "login": {
    // 登录页面相关
  },
  "changePassword": {
    // 修改密码页面相关
  },
  "profile": {
    // 个人中心页面相关
  },
  "chat": {
    // 对话页面相关
  },
  "execution": {
    // 执行面板相关
  },
  "header": {
    // 头部导航相关
  },
  "footer": {
    // 页脚相关
  }
}
```

## 语言切换

用户可以通过 Header 右上角的语言切换器切换语言：
- 🇨🇳 简体中文
- 🇺🇸 English

切换后会：
1. 更新 i18next 语言
2. 保存到 localStorage
3. 刷新页面以更新 Ant Design 组件的语言

## 注意事项

1. **Ant Design 组件**：Ant Design 的内置文本（如日期选择器、分页等）会自动跟随语言切换
2. **localStorage**：语言设置保存在 `localStorage.getItem('language')`
3. **默认语言**：默认为中文 (`zh-CN`)
4. **刷新页面**：切换语言后需要刷新页面以更新 Ant Design 的语言包

## 下一步

建议按照以下顺序完成剩余页面的国际化：

1. Login.tsx（最常用）
2. ChatLayout.tsx 和 ChatWindow.tsx（核心功能）
3. Profile.tsx 和 ChangePassword.tsx（用户相关）
4. ExecutionPanel.tsx（执行面板）
5. Footer.tsx（页脚）

每完成一个页面，测试中英文切换是否正常。
