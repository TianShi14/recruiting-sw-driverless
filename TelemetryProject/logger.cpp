#include "logger.h"

extern "C" {
	#include "fake_receiver.h";
}

string Logger::getMessage() {
	char* msg = new char[MAX_CAN_MESSAGE_SIZE];

	if (can_receive(msg) == -1) {
		return "FFFF#00";
	}
	
	string canMsg(msg);

	cout << "Received Message: " << canMsg << endl;

	return canMsg;
	
}


Parsed Logger::parseMessage(const string& canMsg) {
	Parsed parsed;
	size_t index = 0;

	for (size_t i = 0; i < canMsg.length(); ++i) {
		if ( canMsg[i] == '#' ) {  
			index = i;
			break;
		}
	}
	if (index > 3) {
		return Parsed();
	}
	parsed.id = stoul(canMsg.substr(0, index), nullptr, 16);
	
	parsed.payload.clear();

	string payload = canMsg.substr(index + 1, canMsg.length() - 1);

	if (payload.length() % 2 != 0 || payload.length() > 16) {
		return Parsed();
	}
	for (size_t i = 0; i < payload.length(); i += 2) {
		string payloadByte = payload.substr(i, 2);
		parsed.payload.push_back(stoul(payloadByte, nullptr, 16));
	}

	return parsed;
}

void Logger::newSession() {
	sessionNum++;
	string filename = "../LogSession_" + to_string(sessionNum) + ".txt";
	logFile.open(filename);
}


void Logger::Idle(const Parsed& message) {
	uint8_t prev = NULL;
	if (message.id == 0x0A0) {
		if (message.payload.size() == 2){
			for (const auto& msgByte : message.payload) {
				if ((msgByte == 0x66 && prev == NULL) || (msgByte == 0xFF && prev == NULL)) {
					prev = msgByte;
				}
				else if (msgByte == 0x01 && (prev == 0x66 || prev == 0xFF)) {
					newSession();
					updateLog(message);
					setStats(message.id);
					state = State::RUN;
				}
			}
		}
	}
}

void Logger::Run(const Parsed& message) {
	uint8_t prev = NULL;

	if (message.id == 0x0A0) {
		if (message.payload.size() == 2) {
			for (auto& msgByte : message.payload) {
				if (msgByte == 0x66 && prev == NULL) {
					prev = msgByte;
				}
				else if (msgByte == 0xFF && prev == 0x66) {
					state = State::IDLE;
					logFile.close();
					setStats(message.id);
					updateStats();
					return;
				}
			}
		}
	}
	updateLog(message);
	setStats(message.id);
}

void Logger::updateLog(const Parsed& message) {
	while (!logFile.is_open()) {
		newSession();
	}
	auto seconds = chrono::duration_cast<chrono::seconds>(chrono::system_clock::now().time_since_epoch()).count();

	logFile << dec << "(" << seconds << ") ";
	logFile << uppercase << hex << setw(3) << setfill('0') << message.id << "#";
	for (const auto& payloadByte : message.payload) {
		logFile << setw(2) << setfill('0') << payloadByte;
	}
	logFile << endl;
}

void Logger::setStats(const uint16_t& id) {
	auto now = std::chrono::high_resolution_clock::now();
	auto duration = chrono::duration_cast<chrono::milliseconds>(now - start);

	if (statsId.find(id) != statsId.end()) {
		auto meanT = duration.count() - statsId[id].firstOccurence;

		statsId[id].numMessages++;
		statsId[id].timeMean = (duration.count() - statsId[id].firstOccurence) / (statsId[id].numMessages - 1);
	}
	else {
		statsId.emplace(id, Stat(1, duration.count(), duration.count()));
	}
}

void Logger::updateStats() {
	statsFile << "sep=," << endl;
	statsFile << "ID,number_of_messages,mean_time" << endl;
	for (auto const& element : statsId) {
		ostringstream idLine, statLine;

		idLine << uppercase << hex << setw(3) << setfill('0') << element.first << ",";
		statLine << element.second.numMessages << "," << element.second.timeMean << endl;

		statsFile << idLine.str() << statLine.str();
	}
}

void Logger::execute(){
	while (true) {
		Parsed message = parseMessage(getMessage());
		if (message.id == 0xFFFF) continue;

		if (state == State::IDLE) {
			cout << "IDLE\n";
			Idle(message);
		}
		else if (state == State::RUN) {
			cout << "RUN\n";
			Run(message);
		}
	}
}