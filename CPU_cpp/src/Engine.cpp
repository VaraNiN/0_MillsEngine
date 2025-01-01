#include "Engine.h"
#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>


std::string generateKey(const BoardState& state) {
    std::ostringstream keyStream;
    keyStream << state.blackPieces.to_string()
              << state.whitePieces.to_string()
              << state.isTurnWhite
              << state.placingPhase
              << state.isLateGameWhite
              << state.isLateGameBlack;
    return keyStream.str();
}

void History::saveState(const BoardState& state) {
    history.push_back(state);
}

const std::vector<BoardState>& History::getHistory() const {
    return history;
}