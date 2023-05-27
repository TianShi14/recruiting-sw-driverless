#include "logger.h"

string Logger::getMessage() {
	//idfk how toget the CAN bus bullshit
}


Parsed Logger::parseMessage(const string& msg) {
	Parsed parsed;
	size_t index = 0;

	for (size_t i = 0; i < msg.length(); ++i) {
		if ( msg[i] == '#' ) {  
			index = i;
			break;
		}
	}
	if (index > 3) {
		return parsed;
	}
	parsed.id = stoi(msg.substr(0, index), nullptr, 16);
	
	string payload = msg.substr(index + 1);
	if (payload.length() % 2 != 0) {
		return parsed;
	}
	for (size_t i = 0; i < payload.length(); i += 2) {
		string payloadByte = payload.substr(i, 2);
		parsed.payload.push_back(stoi(payloadByte, nullptr, 16));
	}

	return parsed;
}

void Logger::Idle(Parsed message) {
	uint8_t prev = NULL;

	if (message.id == 0x0A0) {
		if (message.payload.size() == 2){
			for (auto& msgByte : message.payload) {
				if (msgByte == 0x66 || (msgByte == 0xFF && prev == NULL)) {
					prev = msgByte;
				}
				else if (msgByte == 0xFF && prev == 0x66) {
					// probably void since it doesn't make sense to specify to stop in idle
				}
				else if (msgByte == 0x01 && (prev == 0x66 || prev == 0xFF)) {
					state = State::RUN;
					// new session started
				}
			}
		}
	}
}

void Logger::Run(Parsed message) {

}

void Logger::execute(){
	while (true) {
		Parsed message = parseMessage(getMessage());

		if (state == State::IDLE) {
			Idle(message);
		}
		else if (state == State::RUN) {
			Run(message);
		}
	}
}