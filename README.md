chmod 600 biomni.pem


rsync -az --delete \
  --exclude-from=.gitignore \
  -e "ssh -i ./biomni.pem -o StrictHostKeyChecking=accept-new" \
  ./ ubuntu@44.222.116.143:/home/ubuntu/myBiomni




rsync -az --dry-run --itemize-changes --delete \
  --exclude-from=.gitignore \
  -e "ssh -i ./biomni.pem -o StrictHostKeyChecking=accept-new" \
  ./ ubuntu@44.222.116.143:/home/ubuntu/myBiomni
  
如果你只想看哪些文件会动，不想看详细标记：
rsync -az --dry-run --delete \
  --exclude-from=.rsyncignore \
  --exclude-from=.gitignore \
  --out-format='%n' \
  -e "ssh -i ./biomni.pem -o StrictHostKeyChecking=accept-new" \
  ./ ubuntu@44.222.116.143:/home/ubuntu/myBiomni/

同步单个文件：

rsync -az --relative \
  -e "ssh -i ./biomni.pem -o StrictHostKeyChecking=accept-new" \
  client/frontend/src/components/ChatWindow.tsx \
  client/frontend/src/components/ExecutionPanel.tsx \
  client/frontend/src/components/MarkdownContent.tsx \
  client/frontend/src/components/MarkdownContent.tsx \
  client/frontend/src/hooks/useWebSocket.ts \
  client/frontend/src/types/index.ts \
  client/frontend/package.json \
  client/frontend/package-lock.json \
  agent/services/agent_service.py \
  agent/services/callback.py \
  ubuntu@44.222.116.143:/home/ubuntu/myBiomni/

rsync -az --relative \
  -e "ssh -i ./biomni.pem -o StrictHostKeyChecking=accept-new" \
  agent/services/agent_service.py \
  agent/services/callback.py \
  admin/frontend/src/router/routes/index.js \
  admin/frontend/src/views/config/model/index.vue \
  admin/frontend/src/views/knowhow/index.vue \
  admin/frontend/i18n/messages/cn.json \
  admin/frontend/i18n/messages/en.json \
  agent/biomni/config.py \
  agent/biomni/llm.py \
  ubuntu@44.222.116.143:/home/ubuntu/myBiomni/

scp  -i ./biomni.pem  ubuntu@44.222.116.143:/home/ubuntu/myBiomni/agent/log5 .
