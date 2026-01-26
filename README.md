chmod 600 biomni.pem


rsync -az --delete \
  --exclude-from=.gitignore \
  -e "ssh -i ./biomni.pem -o StrictHostKeyChecking=accept-new" \
  ./ ubuntu@44.222.116.143:/home/ubuntu/myBiomni


  scp 