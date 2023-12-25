package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// worker 函数进行文件筛选
func worker(wg *sync.WaitGroup, files <-chan string, fileNameIncludeList, fileNameExcludeList, fileTypes, pathIncludeList, pathExcludeList []string, matchAllIncludes bool, results chan<- string) {
	defer wg.Done()
	for file := range files {
		// 路径过滤
		if !isPathValid(file, pathIncludeList, pathExcludeList) {
			continue
		}

		// 文件名过滤
		fileName := filepath.Base(file)
		//println(fileName)
		if matchAllIncludes {
			if allContains(fileName, fileNameIncludeList) && !anyContains(fileName, fileNameExcludeList) && hasFileType(fileName, fileTypes) {
				results <- file
			}
		} else {
			if anyContains(fileName, fileNameIncludeList) && !anyContains(fileName, fileNameExcludeList) && hasFileType(fileName, fileTypes) {
				results <- file
			}
		}
	}
}

// allContains 检查字符串s是否包含所有子串
func allContains(s string, substrs []string) bool {
	for _, substr := range substrs {
		if !strings.Contains(s, substr) {
			return false
		}
	}
	return true
}

// anyContains 检查字符串s是否包含任何子串
func anyContains(s string, substrs []string) bool {
	for _, substr := range substrs {
		if strings.Contains(s, substr) {
			return true
		}
	}
	return false
}

// hasFileType 检查文件类型
func hasFileType(s string, types []string) bool {
	for _, t := range types {
		if strings.HasSuffix(s, t) {
			return true
		}
	}
	return false
}

// readConfig 读取配置文件
func readConfig(configPath string) (map[string]interface{}, error) {
	var config map[string]interface{}

	file, err := os.Open(configPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	err = decoder.Decode(&config)
	if err != nil {
		return nil, err
	}

	return config, nil
}

// toStringSlice 将interface{}转换为[]string
func toStringSlice(i interface{}) []string {
	var slice []string
	if i != nil {
		for _, item := range i.([]interface{}) {
			slice = append(slice, item.(string))
		}
	}
	return slice
}

// isPathValid 检查路径是否符合包含和排除规则
func isPathValid(path string, includeList, excludeList []string) bool {
	// 包含列表检查
	if len(includeList) > 0 {
		match := false
		for _, include := range includeList {
			if strings.Contains(path, include) {
				match = true
				break
			}
		}
		if !match {
			return false
		}
	}

	// 排除列表检查
	for _, exclude := range excludeList {
		if strings.Contains(path, exclude) {
			return false
		}
	}

	return true
}

func serach(rootDir string) []string {
	// 程序开始时间
	startTime := time.Now()

	var matchedFiles []string

	configPath := "config.json"
	config, err := readConfig(configPath)
	if err != nil {
		fmt.Println("Error reading config file:", err)
		return matchedFiles
	}

	//rootDir := config["path"].(string)
	fileNameIncludeList := toStringSlice(config["fileNameIncludeList"])
	fileNameExcludeList := toStringSlice(config["fileNameExcludeList"])
	fileTypes := toStringSlice(config["fileTypes"])
	pathIncludeList := toStringSlice(config["pathIncludeList"])
	pathExcludeList := toStringSlice(config["pathExcludeList"])
	matchAllIncludes := config["matchAllIncludes"].(bool)
	// 读取新增的通道大小配置
	filesChanSize := int(config["filesChanSize"].(float64)) // JSON中的数字默认为float64
	resultsSize := int(config["resultsSize"].(float64))
	maxGoroutines1 := int(config["maxGoroutines1"].(float64)) // 从配置中读取协程数量

	filesChan := make(chan string, filesChanSize) // 使用配置的大小初始化通道
	results := make(chan string, resultsSize)

	var wg sync.WaitGroup

	for i := 0; i < maxGoroutines1; i++ {
		wg.Add(1)
		go worker(&wg, filesChan, fileNameIncludeList, fileNameExcludeList, fileTypes, pathIncludeList, pathExcludeList, matchAllIncludes, results)
	}

	walkDirStartTime := time.Now()
	err = filepath.WalkDir(rootDir, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			fmt.Println("Error accessing:", path, "; Error:", err)
			return nil
		}
		if !d.IsDir() {
			filesChan <- path
		}
		return nil
	})
	if err != nil {
		fmt.Println("WalkDir error:", err)
	}
	close(filesChan)
	walkDirEndTime := time.Now()
	fmt.Printf("filepath.WalkDir execution time: %v\n", walkDirEndTime.Sub(walkDirStartTime))

	go func() {
		wg.Wait()
		close(results)
	}()

	for file := range results {
		matchedFiles = append(matchedFiles, file)
	}

	return matchedFiles

	jsonResult, err := json.Marshal(matchedFiles)
	if err != nil {
		fmt.Println("JSON Marshal Error:", err)
		return matchedFiles
	}

	file, err := os.Create("paths.json")
	if err != nil {
		fmt.Println("Error creating JSON file:", err)
		return matchedFiles
	}
	defer file.Close()

	_, err = file.Write(jsonResult)
	if err != nil {
		fmt.Println("Error writing JSON to file:", err)
		return matchedFiles
	}

	fmt.Println("JSON data successfully saved to 'paths.json'")

	// 程序结束时间
	endTime := time.Now()
	fmt.Printf("Total execution time: %v\n", endTime.Sub(startTime))

	return matchedFiles
}

func main() {
	// 假设json文件名为data.json
	jsonFile, err := os.Open("paths1.json")
	if err != nil {
		fmt.Println("Error opening JSON file:", err)
		return
	}
	defer jsonFile.Close()

	// 读取文件内容
	byteValue, _ := ioutil.ReadAll(jsonFile)

	// 使用interface{}解析JSON数据
	var result []map[string]interface{}
	err = json.Unmarshal(byteValue, &result)
	if err != nil {
		fmt.Println("Error parsing JSON:", err)
		return
	}

	// 提取path字段的值到列表中
	var paths []string
	for _, item := range result {
		aps, ok := item["APS"].(map[string]interface{})
		if !ok {
			fmt.Println("Error: APS field is not a map")
			continue
		}
		path, ok := aps["path"].([]interface{})
		if !ok {
			fmt.Println("Error: path field is not an array")
			continue
		}
		for _, p := range path {
			pathStr, ok := p.(string)
			if !ok {
				fmt.Println("Error: path item is not a string")
				continue
			}
			paths = append(paths, pathStr)
		}
	}

	var matchedFiles []string
	for _, path := range paths {
		fmt.Println("serach:", path)
		matchedFiles = append(matchedFiles, serach(path)...)
	}

	jsonResult, err := json.Marshal(matchedFiles)
	if err != nil {
		fmt.Println("JSON Marshal Error:", err)
	}

	file, err := os.Create("paths.json")
	if err != nil {
		fmt.Println("Error creating JSON file:", err)
	}
	defer file.Close()

	_, err = file.Write(jsonResult)
	if err != nil {
		fmt.Println("Error writing JSON to file:", err)
	}

	fmt.Println("JSON data successfully saved to 'paths.json'")
}
