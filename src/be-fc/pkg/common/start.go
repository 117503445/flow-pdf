package common

import (
	"github.com/117503445/flow-pdf-be-fc/pkg/config"
	"github.com/117503445/flow-pdf-be-fc/pkg/oss"
)

func Start() {
	config.ReadConfig()
	oss.InitGlobalManager()
}
