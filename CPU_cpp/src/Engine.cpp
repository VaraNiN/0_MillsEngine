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

// Checks which game phase it is
void checkPhase(BoardState& state) {
    if (state.moveNumber >= 18) {
        state.placingPhase = false;
    } else {
        state.placingPhase = true;
    }

    if (!state.placingPhase){
        if (state.whitePieces.count() == 3) {
            state.isLateGameWhite = true;
        } else {
            state.isLateGameWhite = false;
        }
        if (state.blackPieces.count() == 3) {
            state.isLateGameBlack = true;
        } else {
            state.isLateGameBlack = false;
        }
    }
}

// Adds a single piece to the board and appends that state to history
void inputAdd(BoardState& state, History& history) {
    std::vector<int> position = runMillsBoard(state, 1);
    
    if (position[0] == -1) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            state = hist.at(hist.size() - 2);
            history.deleteLastEntry();
        } catch (const std::out_of_range& e) {
            std::cout << "Not enough history to go back!" << std::endl;
        }
    } else if (position[0] == -2) {
        std::vector<BoardState> hist = history.getHistory();
        try {
            state = hist.at(hist.size() - 3);
            history.deleteLastEntry();
            history.deleteLastEntry();
        } catch (const std::out_of_range& e) {
            std::cout << "Not enough history to go back two steps!" << std::endl;
        }
    } else if (position[0] == -3) {
        exit(0);
    } else if (state.whitePieces[position[0]] != 0 || state.blackPieces[position[0]] != 0) {
        std::cout << "There is already a piece there!" << std::endl;
        inputAdd(state, history);
    } else {
        if (state.isTurnWhite) {
            state.whitePieces.set(position[0]);
        } else {
            state.blackPieces.set(position[0]);
        }
        state.isTurnWhite = !state.isTurnWhite;
        state.moveNumber ++;
        checkPhase(state);
        history.saveState(state);
    }
}