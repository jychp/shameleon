package main

import (
	"net/http"
	"net/url"
	"io/ioutil"
	"encoding/json"
	"strings"
	"bytes"
	"strconv"
	"time"
)

type GetEndpointFormat struct {
	Data struct {
		Result []struct {
			Values [][]string `json:"values"`
		} `json:"result"`
	} `json:"data"`
}

type ValuesData struct {
	Message string `json:"message"`
}

func CustomGetPackets(p *Provider) ([]Packet, error) {
	var packets []Packet
	// Get data	from server
	params := url.Values{}
	params.Add("query", "{" + p.Config.Custom["label"] + "=\"" + p.Config.Custom["label_in"] + "\"}")
	var startTs int64
	if p.LastPacket == 0 {
		startTs = time.Now().UnixNano()
	} else {
		startTs = p.LastPacket + 1000000
	}
	startFloat := float64(startTs) / 1000000000
	endFloat := float64(time.Now().UnixNano()) / 1000000000
	params.Add("start", strconv.FormatFloat(startFloat, 'f', 6, 64))
	params.Add("end", strconv.FormatFloat(endFloat, 'f', 6, 64))
	params.Add("limit", "1000")
	params.Add("direction", "FORWARD")
	req, _ := http.NewRequest("GET", p.Config.Custom["url"] + "/loki/api/v1/query_range?" + params.Encode(), nil)
	req.Header.Add("Authorization","Basic " + basicAuth(p.Config.Custom["user"],p.Config.Custom["token"]))
	client := &http.Client{
		CheckRedirect: 	func(req *http.Request, via []*http.Request) error {
							return http.ErrUseLastResponse
						},
	}
	resp, err := client.Do(req)
	if err != nil {
		println("ERROR: Failed to connect to server", err.Error())
		return []Packet{}, err
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		println("ERROR: Failed to read server response", err.Error())
		return []Packet{}, err
	}
	var rawData GetEndpointFormat
	err = json.Unmarshal([]byte(body), &rawData)
	if err != nil {
		println("ERROR: Failed to parse server response", err.Error())
		return []Packet{}, err
	}
	if len(rawData.Data.Result) == 0 {
		return []Packet{}, nil
	}
	for _, value := range rawData.Data.Result[0].Values {
		var packetData ValuesData
		err = json.Unmarshal([]byte(value[1]), &packetData)
		lineTs, _ := strconv.ParseInt(value[0], 10, 64)
		p.LastPacket = Max(p.LastPacket, lineTs)
		if err != nil {
			println("ERROR: Failed to parse server response", err.Error())
			return []Packet{}, err
		}
		packet, err := ParsePacket(packetData.Message, p.Config)
		if err != nil {
			return []Packet{}, err
		}
		packets = append(packets, packet)
	}
	return packets, nil
}

func CustomSendPackets(p *Provider, packets []Packet) error {
	results := []string{}
	startTs := time.Now().UnixNano() - int64(len(packets))
	for i, packet := range packets {
		lineTs := startTs + int64(i)
		results = append(results, "[\"" + Int64toString(lineTs) + "\",\"{\\\"message\\\":\\\"" + packet.Format() + "\\\"}\"]")
	}
	payload := "{\"streams\": [{\"stream\": {\"" + p.Config.Custom["label"] + "\": \"" + p.Config.Custom["label_out"] + "\"},\"values\": [" + strings.Join(results, ",") + "]}]}"
	req, _ := http.NewRequest("POST", p.Config.Custom["url"] + "/loki/api/v1/push", bytes.NewBuffer([]byte(payload)))
	req.Header.Add("Authorization","Basic " + basicAuth(p.Config.Custom["user"],p.Config.Custom["token"]))
	req.Header.Add("Content-Type", "application/json")
	client := &http.Client{
		CheckRedirect: 	func(req *http.Request, via []*http.Request) error {
							return http.ErrUseLastResponse
						},
	}
	_, err := client.Do(req)
	if err != nil {
		println("ERROR: Failed to connect to server", err.Error())
		return err
	}
	return nil
}
