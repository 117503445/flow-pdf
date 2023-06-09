package oss

import (
	"github.com/117503445/flow-pdf-be-fc/pkg/config"
	"github.com/aliyun/aliyun-oss-go-sdk/oss"
)

type managerConfig struct {
	Endpoint        string
	Bucket          string
	AccessKeyId     string
	AccessKeySecret string
}

type manager struct {
	config *managerConfig
	client *oss.Client
	bucket *oss.Bucket
}

var GlobalManager *manager

func InitGlobalManager() {
	GlobalManager = NewManager(
		&managerConfig{
			Endpoint:        config.GlobalConfig.OSS.Endpoint,
			Bucket:          config.GlobalConfig.OSS.Bucket,
			AccessKeyId:     config.GlobalConfig.OSS.Ak,
			AccessKeySecret: config.GlobalConfig.OSS.Sk,
		},
	)
}

func NewManager(config *managerConfig) *manager {
	client, err := oss.New(config.Endpoint, config.AccessKeyId, config.AccessKeySecret)
	if err != nil {
		panic(err)
	}
	bucket, err := client.Bucket(config.Bucket)
	if err != nil {
		panic(err)
	}

	return &manager{
		config: config,
		client: client,
		bucket: bucket,
	}
}

func (m *manager) Put(objectKey string, filePath string) error {
	return m.bucket.PutObjectFromFile(objectKey, filePath)
}
