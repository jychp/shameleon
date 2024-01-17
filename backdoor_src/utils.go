package main

import (
	"os"
	"encoding/base64"
	"strconv"
)

func Fail(errorcode int) {
	println("error", errorcode)
	os.Exit(1)
}

func basicAuth(username, password string) string {
	auth := username + ":" + password
	return base64.StdEncoding.EncodeToString([]byte(auth))
}

func FileExists(path string) bool {
	_, err := os.Stat(path)
	if err == nil {
		return true
	}
	if os.IsNotExist(err) {
		return false
	}
	return true
}

func Max(x int64, y int64) int64 {
	if x < y {
		return y
	}
	return x
}

func Int64toString(x int64) string {
	y := int(x)
	if int64(y) != x {
		return "0"
	}
	return strconv.Itoa(y)
}
