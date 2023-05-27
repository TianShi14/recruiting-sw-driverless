#pragma once

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <ctime>

using namespace std;

struct Parsed {
    uint16_t id;
    vector<uint8_t> payload;
};

class Logger {
public:

    Logger() : state(State::IDLE) {}
    void execute();

private:

    enum class State { IDLE, RUN };

    State state;
    
    string getMessage();
    Parsed parseMessage(const string& msg);
    void Idle(Parsed message);
    void Run(Parsed message);
};