package config

import "github.com/kjzz/viper"

type OSSConfig struct {
	Ak       string
	Sk       string
	Endpoint string
	Bucket   string
}

type Config struct {
	OSS *OSSConfig
}

var GlobalConfig *Config


func ReadConfig() {
	v := viper.New()
	v.SetConfigName("config")
	v.SetConfigType("toml")
	v.AddConfigPath("./config")
	if err := v.ReadInConfig(); err != nil {
		panic(err)
	}
	if err := v.Unmarshal(&GlobalConfig); err != nil {
		panic(err)
	}
}
