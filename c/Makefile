CXX = g++
CXXFLAGS = -std=c++11 -Wall -O2
LDFLAGS = -lncurses

TARGET = termonal
SOURCES = main.cpp termonal.cpp
HEADERS = termonal.hpp
OBJECTS = $(SOURCES:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

.PHONY: all clean
