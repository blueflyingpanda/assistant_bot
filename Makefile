SRC_DIR := src
BUILD_DIR := build
BUILD_ARC := build.zip

build:
	mkdir -p $(BUILD_DIR)
	cp -r $(SRC_DIR)/* $(BUILD_DIR)
	cp data.json $(BUILD_DIR)
	cp requirements.txt $(BUILD_DIR)
	zip -j $(BUILD_ARC) $(BUILD_DIR)/*
	rm -rf $(BUILD_DIR)

clean:
	rm -rf $(BUILD_ARC)

# This is a phony target, meaning it doesn't represent a file
.PHONY: build clean