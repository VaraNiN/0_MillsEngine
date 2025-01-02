#include "Engine.h"
#include "GUI.h"
#include <bitset>
#include <string>
#include <sstream>
#include <vector>
#include <cstdint>
#include <iostream>
#include <cstdlib>


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

void History::deleteEntry(size_t index) {
    if (index < history.size()) {
        history.erase(history.begin() + index);
    } else {
        std::cout << "Index out of range!" << std::endl;
    }
}

void History::deleteLastEntry() {
    if (!history.empty()) {
        history.pop_back();
    } else {
        std::cout << "History is empty!" << std::endl;
    }
}

void History::clearHistory() {
    history.clear();
}

// Checks which game phase it is and if position is valid
void checkPhase(BoardState& state) {
    if ((state.whitePieces & state.blackPieces).any()) {
        throw std::runtime_error("Error: Two pieces occupy the same position!");
    }

    state.placingPhase = (state.moveNumber < 18);

    if (!state.placingPhase) {
        state.isLateGameWhite = (state.whitePieces.count() == 3);
        state.isLateGameBlack = (state.blackPieces.count() == 3);
    }
}