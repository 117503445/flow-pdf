package main

import (
	"fmt"

	"github.com/117503445/flow-pdf-be-fc/pkg/common"
	"github.com/117503445/flow-pdf-be-fc/pkg/oss"
)

func main() {
	fmt.Println("upload")
	common.Start()

	err := oss.GlobalManager.Put("input/bitcoin.pdf", "../data/bitcoin.pdf")
	if err != nil {
		panic(err)
	}
}
