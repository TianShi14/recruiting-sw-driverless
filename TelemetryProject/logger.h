#pragma once

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cstdint>
#include <unordered_map>
#include <map>
#include <chrono>

using namespace std;
using timer = std::chrono::high_resolution_clock::time_point;

struct Parsed {
    uint16_t id;
    vector<uint16_t> payload; // theoretically a uint8_t should be enough, but string to uint conversion through stoi, stoul, stringstream etc. always causes overflow

    Parsed() : id(0xFFFF), payload(1, 0x00) {};
};

struct Stat {
    unsigned numMessages;
    double firstOccurence, timeMean;

    Stat() : numMessages(0), firstOccurence(0), timeMean(0) {};
    Stat(unsigned num, double first, double mean) : numMessages(num), firstOccurence(first), timeMean(mean) {};
};

class Logger {
public:

    Logger() : state(State::IDLE), sessionNum(0), start(std::chrono::high_resolution_clock::now()), statsFile("../statistics.csv") {};

    void execute();

private:

    enum class State { IDLE, RUN };

    State state;
    unsigned sessionNum;
    unordered_map<uint16_t, Stat> statsId;
    timer start;
    ofstream logFile, statsFile;

    
    string getMessage();
    Parsed parseMessage(const string& canMsg);
    void Idle(const Parsed& message);
    void Run(const Parsed& message);
    void newSession();
    void updateLog(const Parsed& message);
    void setStats(const uint16_t& id);
    void updateStats();
};
