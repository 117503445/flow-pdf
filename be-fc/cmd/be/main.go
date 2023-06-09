/*
 * Copyright 2022 CloudWeGo Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"fmt"
	"io"
	"os"

	"github.com/117503445/flow-pdf-be-fc/pkg/common"
	"github.com/117503445/flow-pdf-be-fc/pkg/oss"
	"github.com/cloudwego/hertz/pkg/app"
	"github.com/cloudwego/hertz/pkg/app/server"
	"github.com/cloudwego/hertz/pkg/protocol/consts"
)

func main() {
	common.Start()

	// WithMaxRequestBodySize can set the size of the body
	h := server.Default(server.WithHostPorts("0.0.0.0:8080"), server.WithMaxRequestBodySize(20<<20))

	h.GET("/", func(ctx context.Context, c *app.RequestContext) {
		c.JSON(consts.StatusOK, "Hello from flow-pdf")
	})

	h.POST("/api/task", func(ctx context.Context, c *app.RequestContext) {
		// single file
		fileHeader, _ := c.FormFile("f")
		if fileHeader == nil {
			c.JSON(consts.StatusOK, map[string]interface{}{
				"code":    2,
				"message": "f not found",
				"data":    map[string]interface{}{},
			},
			)
		}

		file, err := fileHeader.Open()
		if err != nil {
			c.JSON(consts.StatusOK, map[string]interface{}{
				"code":    1,
				"message": "Failed",
				"data": map[string]interface{}{
					"err": err.Error(),
				},
			},
			)
		}

		buf := new(bytes.Buffer)
		_, err = io.Copy(buf, file)
		if err != nil {
			c.JSON(consts.StatusOK, map[string]interface{}{
				"code":    1,
				"message": "Failed",
				"data": map[string]interface{}{
					"err": err.Error(),
				},
			},
			)
		}

		h := sha256.New()
		h.Write(buf.Bytes())
		sha256sum := fmt.Sprintf("%x", h.Sum(nil))
		taskID := sha256sum

		err = os.WriteFile(fmt.Sprintf("./%s.pdf", taskID), buf.Bytes(), 0644)
		if err != nil {
			c.JSON(consts.StatusOK, map[string]interface{}{
				"code":    1,
				"message": "Failed",
				"data": map[string]interface{}{
					"err": err.Error(),
				},
			},
			)
		}

		err = oss.GlobalManager.Put(fmt.Sprintf("input/%s.pdf", taskID), fmt.Sprintf("./%s.pdf", taskID))
		if err != nil {
			c.JSON(consts.StatusOK, map[string]interface{}{
				"code":    2,
				"message": "upload fail",
				"data": map[string]interface{}{
					"err": err.Error(),
				},
			},
			)
		}

		c.JSON(consts.StatusOK, map[string]interface{}{
			"code":    0,
			"message": "Success",
			"data": map[string]interface{}{
				"taskID": taskID,
			},
		})
	})

	h.Spin()
}
