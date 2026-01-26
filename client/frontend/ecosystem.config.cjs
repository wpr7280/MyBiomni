// PM2 配置文件 - Biomni Client Frontend
// 使用 .cjs 扩展名以支持 CommonJS 格式
module.exports = {
  apps: [
    {
      name: 'biomni-client-frontend',
      script: 'npx',
      args: 'vite --mode development --port 3100 --host 0.0.0.0',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        PORT: 3100,
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      time: true,
    },
  ],
};
