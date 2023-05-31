#!/bin/bash

# 获取最近的标签名称，如果不存在则返回空字符串
tag=$(git describe --tags --abbrev=0 HEAD 2>/dev/null || echo "")

if [ -n "$tag" ]; then
  # 如果存在标签，则写入标签名称
  echo -n "$tag" > ./flow-pdf/git.txt
else
  # 如果不存在标签，则写入提交哈希值
  commit_hash=$(git rev-parse HEAD)
  echo -n "dev-$commit_hash" > ./flow-pdf/git.txt
fi