#include <stdio.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <ctime>

using namespace std;

extern "C" {
    #include "fake_receiver.h"
}
#include "logger.h"

int main(void) {

    cout << "Welcome to Project 2" << endl;

    Logger logger = Logger();

    if (open_can("../candump.log") == 0) {
        logger.execute();
    }

    close_can();

    return 0;
}