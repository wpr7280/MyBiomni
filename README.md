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
  agent/biomni/agent/a1.py \
  agent/services/agent_service.py \
  agent/services/callback.py \
  ubuntu@44.222.116.143:/home/ubuntu/myBiomni/

rsync -az --relative \
  -e "ssh -i ./biomni.pem -o StrictHostKeyChecking=accept-new" \
  agent/services/callback.py \
 agent/biomni/agent/a1.py \
 client/frontend/src/components/ExecutionPanel.tsx \
  ubuntu@44.222.116.143:/home/ubuntu/myBiomni/

scp  -i ./biomni.pem  ubuntu@44.222.116.143:/home/ubuntu/myBiomni/agent/log5 .
git log -10